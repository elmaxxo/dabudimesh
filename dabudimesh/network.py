from router import Router
from utils import create_connection
from message import Message
from config import MSG_MAX_LEN


class NetworkInterfaceController:
    def __init__(self, address):
        self.router = Router(address)

    async def connect_with(self, addr):
        sock = create_connection(addr)
        if sock is None:
            return sock

        greeting = Message("greeting", self.router.address, addr)
        sock.sendall(greeting.encode())

        message = Message.decode(sock.recv(MSG_MAX_LEN))
        assert message.get_command() == "routes"
        addr_to = message.get_source()
        routing_table = message.get_param("routing_table")
        self.router.add_routes(addr_to, routing_table.keys())

        self.broadcast_route(addr)
        self.router.add_neighbor(addr, sock)
        self.send_routes_to(addr)
        return sock

    async def send_text(self, dst_addr, text):
        message = Message("text", self.router.address, dst_addr, {"text": text})
        self.router.send(message)

    def broadcast_route(self, address):
        for neighbor_addr in self.router.neighbors.keys():
            add_route_msg = Message(
                "add_route", self.router.address, neighbor_addr, {"address": address}
            )
            self.router.send(add_route_msg)

    def send_routes_to(self, neighbor_addr):
        routes = Message(
            "routes",
            self.router.address,
            neighbor_addr,
            {"routing_table": self.router.routing_table},
        )
        self.router.send(routes)

    def handle_message(self, address):
        message = self.router.route_pending()
        if message is None:
            return None

        if message.get_command() == "text":
            text = message.get_param("text")
            return f"Message from {message.get_source()}: {text}"

        elif message.get_command() == "add_route":
            address = message.get_param("address")
            if address not in self.router.available_addresses():
                self.router.add_route(address, message.get_source())
                self.broadcast_route(address)

        elif message.get_command() == "routes":
            addr_to = message.get_source()
            routing_table = message.get_param("routing_table")
            self.router.add_routes(addr_to, routing_table.keys())

        else:
            return f"Can't handle command: {message.get_command()}"

        return None

    def accept_connection(self, server):
        neighbor = server.accept()[0]
        message = Message.decode(neighbor.recv(MSG_MAX_LEN))
        assert message.get_command() == "greeting"
        neighbor_address = message.get_source()

        self.broadcast_route(neighbor_address)
        self.router.add_neighbor(neighbor_address, neighbor)
        self.send_routes_to(neighbor_address)

        return (neighbor, neighbor_address)
