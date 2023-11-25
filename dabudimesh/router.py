MSG_MAX_LEN = 4096


class Router:
    def __init__(self, address, listener):
        self.listener = listener
        self.routing_table = {}
        self.address = address

    def add_connection(self, address, socket):
        # TODO: inform neighbors recursively
        socket.sendall(bytes(self.address, "utf-8"))
        self.routing_table[address] = socket

    def send(self, address, message):
        # TODO: raise an error if not found
        socket = self.routing_table[address]
        socket.sendall(bytes(f"{address}:{message}", "utf-8"))

    def process_message_from(self, socket):
        message = socket.recv(MSG_MAX_LEN).decode()
        [address, text] = message.split(":", maxsplit=1)
        if address == self.address:
            print(f"Read: {text}")
            return text
        else:
            # TODO: redirect if self.address != message.address
            None

    def accept(self):
        (socket, _) = self.listener.accept()
        address = socket.recv(MSG_MAX_LEN).decode("utf-8")
        print("New connection from ", address)
        self.routing_table[address] = socket
        return (socket, address)
