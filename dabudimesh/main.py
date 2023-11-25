from router import Router
from utils import create_server, socket_address
from shell import DabudiShell, _on_read
import asyncio


def _on_accept(router):
    (sock, _) = router.accept()
    asyncio.get_event_loop().add_reader(sock, _on_read, sock, router)


def main():
    listener = create_server()
    address = socket_address(listener)
    router = Router(address, listener)

    loop = asyncio.new_event_loop()
    shell = DabudiShell(router, loop)
    loop.run_in_executor(None, shell.cmdloop)
    loop.add_reader(listener, _on_accept, router)
    loop.run_forever()


if __name__ == "__main__":
    main()
