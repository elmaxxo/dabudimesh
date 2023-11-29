from utils import create_connection
import bluetooth
from cmd import Cmd


def _on_read(sock, router):
    message = router.process_message_from(sock)
    if message is not None:
        print(message)


class DabudiShell(Cmd):
    type_help = "Type help or ? to list commands."
    intro = "Welcome to the DabudiMesh shell. " + type_help + "\n"
    prompt = "(dabudi) "

    def __init__(self, router, event_loop):
        super().__init__()
        self.router = router
        self.event_loop = event_loop

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
            self.router.add_connection(addr, sock)
            if self.event_loop is not None:
                self.event_loop.add_reader(sock, _on_read, sock, self.router)

    def do_message(self, arg):
        "message [addr] [msg] : Send message (msg) to node with address (addr)"
        args = self.__process(arg, 2)
        if args is not None:
            addr = args[0]
            message = args[1]
            self.router.send_text(addr, message)

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
