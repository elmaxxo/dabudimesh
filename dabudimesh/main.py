from router import Router
import asyncio
import sys
import random
import os
import socket


EXIT_COMMAND = "\\exit"
CONNECT_COMMAND = "\\connect"
MESSAGE_COMMAND = "\\message"


def _on_command(sock, router):
    command = sock.read()
    command = command.strip()
    print(f"Processing command: {command}")
    if command.startswith(EXIT_COMMAND):
        print("Got exit command")
        exit()

    elif command.startswith(CONNECT_COMMAND):
        print("Got connect command")
        port = int(command.split(" ")[1])
        sock = socket.create_connection(("localhost", port))
        router.add_connection(port, sock)
        asyncio.get_event_loop().add_reader(sock, _on_read, sock, router)

    elif command.startswith(MESSAGE_COMMAND):
        print("Got message command")
        [_, address, text] = command.split(" ", maxsplit=2)
        router.send(int(address), text)

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
    random.seed(str(os.times()))
    port = random.randint(1000, 5000)
    print(f"port:{port}")
    listener = socket.create_server(("localhost", port))
    router = Router(port, listener)

    loop = asyncio.new_event_loop()
    loop.add_reader(listener, _on_accept, router)
    loop.add_reader(sys.stdin, _on_command, sys.stdin, router)
    loop.run_forever()


if __name__ == "__main__":
    main()
