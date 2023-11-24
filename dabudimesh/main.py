from router import Router
from utils import create_server, create_connection, socket_address
import asyncio
import sys
import bluetooth
from config import IS_USING_BLUETOOTH

IS_USING_BLUETOOTH = False

EXIT_COMMAND = "\\exit"
CONNECT_COMMAND = "\\connect"
MESSAGE_COMMAND = "\\message"
SCAN_COMMAND = "\\scan"


def _on_command(sock, router):
    command = sock.readline()
    command = command.strip()
    print(f"Processing command: {command}")
    if command.startswith(EXIT_COMMAND):
        print("Got exit command")
        exit()

    elif command.startswith(CONNECT_COMMAND):
        print("Got connect command")
        addr = command.split(" ")[1]
        sock = create_connection(addr, IS_USING_BLUETOOTH)
        router.add_connection(addr, sock)
        asyncio.get_event_loop().add_reader(sock, _on_read, sock, router)

    elif command.startswith(MESSAGE_COMMAND):
        print("Got message command")
        [_, address, text] = command.split(" ", maxsplit=2)
        router.send(address, text)

    elif command.startswith(SCAN_COMMAND):
        print("Got scan command")
        devices = dict(bluetooth.discover_devices(lookup_names=True))
        devices = {devices[k]: k for k in devices}

        print(f"Found {len(devices)} devices")
        for name in devices:
            print(devices[name], name)

    else:
        print(f"Can't handle command {command}")


def _on_read(sock, router):
    text = router.process_message_from(sock)
    if text is not None:
        print(text)


def _on_accept(router):
    (sock, _) = router.accept()
    asyncio.get_event_loop().add_reader(sock, _on_read, sock, router)


def main():
    listener = create_server(IS_USING_BLUETOOTH)
    address = socket_address(listener, IS_USING_BLUETOOTH)
    router = Router(address, listener)
    print("Our address is ", address)

    loop = asyncio.new_event_loop()
    loop.add_reader(listener, _on_accept, router)
    loop.add_reader(sys.stdin, _on_command, sys.stdin, router)
    loop.run_forever()


if __name__ == "__main__":
    main()
