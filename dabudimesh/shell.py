import asyncio
from utils import create_connection
import bluetooth
from cmd import Cmd
from router import Router
from utils import create_server
from message import Message


def _on_read(address, router: Router):
    try:
        message = router.route_pending()
        if message is None:
            return

        if message.get_command() == "text":
            print(message.get_params()["text"])
        else:
            print(f"Can't handle command: {message.get_command()}")

    except Exception:
        print(f"Router {address} disconnected")
        # TODO: Handle it properly.
        asyncio.get_event_loop().stop()
        exit()


def _on_accept(server, router: Router):
    neighbor = server.accept()[0]
    message = Message.decode(neighbor.recv(1337))
    assert message.get_command() == "greeting"
    neighbor_address = message.get_source()
    router.add_neighbor(neighbor_address, neighbor)
    asyncio.get_event_loop().add_reader(neighbor, _on_read, neighbor_address, router)


class DabudiShell(Cmd):
    type_help = "Type help or ? to list commands."
    intro = "Welcome to the DabudiMesh shell. " + type_help + "\n"
    prompt = "(dabudi) "

    def __init__(self, router: Router, event_loop):
        super().__init__()
        self.router = router
        self.event_loop = event_loop

        router_listener = create_server(router.address)
        if event_loop is not None:
            event_loop.add_reader(router_listener, _on_accept, router_listener, router)

    def do_exit(self, arg):
        "exit : Terminate this program"
        self.__process(arg, 0)
        print("Thank you for using DabudiMesh")
        if self.event_loop is not None:
            self.event_loop.stop()
        return True

    # TODO: add disconnect command
    def do_connect(self, arg):
        "connect [addr] : Connect to node with specified address (addr)"
        args = self.__process(arg, 1)
        if args is not None:
            addr = args[0]
            sock = create_connection(addr)
            greeting = Message("greeting", self.router.address, addr)
            sock.sendall(greeting.encode())
            self.router.add_neighbor(addr, sock)

            if self.event_loop is not None:
                self.event_loop.add_reader(sock, _on_read, addr, self.router)

    def do_message(self, arg):
        "message [addr] [msg] : Send message (msg) to node with address (addr)"
        args = self.__process(arg, 2)
        if args is not None:
            destination = args[0]
            text = args[1]
            message = Message("text", self.router.address, destination, {"text": text})
            self.router.send(message)

    def do_scan(self, arg):
        "scan : Discover nearby bluetooth devices"
        args = self.__process(arg, 0)
        if args is not None:
            devices = dict(bluetooth.discover_devices(lookup_names=True))
            devices = {devices[k]: k for k in devices}
            print(f"Found {len(devices)} devices")
            for name in devices:
                print(devices[name], name)

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
        print(f"Our address is {self.router.address}")
