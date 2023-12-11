from mesh import MeshNetworkNode
import bluetooth
from cmd import Cmd
from threading import Thread
from aescypher import AESCipher
from time import sleep


class DabudiShell(Cmd):
    type_help = "Type help or ? to list commands."
    intro = "Welcome to the DabudiMesh shell. " + type_help + "\n"
    prompt = "(dabudi) "

    def __init__(self, node: MeshNetworkNode, messages: list = None):
        super().__init__()
        self.node = node
        self.shed_thread = Thread(
            target=self.__shed_messages, args=(messages,), daemon=True
        )
        self.shed_thread.start()

    def do_exit(self, arg):
        "exit : Terminate this program"
        self.__process(arg, 0)
        self.node.stop()
        return True

    # TODO: add disconnect command
    def do_connect(self, arg):
        "connect [addr] : Connect to node with specified address (addr)"
        args = self.__process(arg, 1)
        if args is not None:
            addr = args[0]
            connected = self.node.connect_with(addr)
            if not connected:
                print(f"Refused connection to {addr}")

    def do_message(self, arg):
        "message [addr] [msg] : Send message (msg) to node with address (addr)"
        args = self.__process(arg, 2)
        if args is not None:
            destination = args[0]
            text = args[1]
            if destination in self.node.nic.shared_keys:
                cypher = AESCipher(self.node.nic.shared_keys[destination])
                message_encrypted = cypher.encrypt(text).decode("utf-8")
                print(f"Message encrypted: {message_encrypted}")
                text = message_encrypted

            self.node.send_text(destination, text)

    def do_secure(self, arg):
        "secure [addr] : Security channel creating with address (addr)"
        args = self.__process(arg, 1)
        if args is not None:
            destination = args[0]
            self.node.send_public_key(destination)

    def do_scan(self, arg):
        "scan : Discover nearby bluetooth devices"
        args = self.__process(arg, 0)
        if args is not None:
            devices = dict(bluetooth.discover_devices(lookup_names=True))
            devices = {devices[k]: k for k in devices}
            print(f"Found {len(devices)} devices")
            for name in devices:
                print(devices[name], name)

    def do_routes(self, arg):
        "routes : Get list of routes"
        args = self.__process(arg, 0)
        if args is not None:
            routes = self.node.get_routing_table()
            print(f"There are {len(routes)} routes")
            print("{:<30} {:<30}".format("address", "neighbor"))
            for addr_from in routes:
                print("{:<30} {:<30}".format(addr_from, routes[addr_from]))

    def __process(self, arg, num):
        args = arg.split(" ", maxsplit=num - 1) if len(arg) else arg
        args_len = len(args)
        if args_len == num:
            return args

        print(
            f"This command have a number of {num} arguments but {args_len} were given"
        )
        print(self.type_help)
        return None

    def preloop(self):
        print(f"Our address is {self.node.get_address()}")

    def postloop(self):
        print("Thank you for using DabudiMesh")

    def __shed_messages(self, messages):
        while messages is not None:
            if len(messages):
                print(messages.pop(0))
            sleep(0.1)
