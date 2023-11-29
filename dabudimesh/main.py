from router import Router
from shell import DabudiShell
import asyncio
from utils import create_server, socket_address


def main():
    # TODO: wrap router and listener in ConfigurableNone,
    # shell shouldn't register callbacks and listen to socket
    listener = create_server()
    address = socket_address(listener)
    router = Router(address)

    loop = asyncio.new_event_loop()
    shell = DabudiShell(router, loop, listener)
    loop.run_in_executor(None, shell.cmdloop)
    loop.run_forever()


if __name__ == "__main__":
    main()
