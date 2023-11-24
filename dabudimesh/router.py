# from email import message
from message import Message

MSG_MAX_LEN = 4096


class Router:
    def __init__(self, address, listener):
        self.listener = listener
        self.routing_table = {}
        self.address = address

    def add_connection(self, address, socket):
        # TODO: inform neighbors recursively
        self.routing_table[address] = socket
        self.send_connection(address, self.address)

    def send(self, message):
        socket = self.routing_table[message.get_destination()]
        socket.sendall(message.encode())

    def send_message(self, destination, text):
        message = Message("message", self.address, destination, {"text": text})
        print(message)
        self.send(message)

    def send_connection(self, destination, address):
        message = Message("connection", self.address, destination, {"address": address})
        self.send(message)

    def process_message_from(self, socket):
        parameters = Message.decode(socket.recv(MSG_MAX_LEN).decode("utf-8"))

        optional = {}
        additional_parameters = {"text", "address", "previous"}
        for key in additional_parameters:
            if key in parameters["params"]:
                optional[key] = parameters["params"][key]

        message = Message(
            parameters["command"],
            parameters["source"],
            parameters["destination"],
            optional,
        )
        if message.get_destination() == self.address:
            if message.get_command() == "message":
                return message.get_params()["text"]
            elif message.get_command == "connection":
                return message.get_params()["address"]
            else:
                return None
        else:
            # TODO: redirect if self.address != message.address
            None

    def read_message_from(socket):
        message = Message.decode(socket.recv(MSG_MAX_LEN).decode("utf-8"))
        return message

    def accept(self):
        (socket, _) = self.listener.accept()
        address = Message.decode(socket.recv(MSG_MAX_LEN).decode("utf-8"))["params"][
            "address"
        ]
        print("New connection from ", address)
        self.routing_table[address] = socket
        return (socket, address)
