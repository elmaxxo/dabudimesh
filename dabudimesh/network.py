from router import Router
from utils import create_connection
from message import Message
from config import MSG_MAX_LEN
from aescypher import AESCipher
from kyber.kyber import Kyber768


class NetworkInterfaceController:
    def __init__(self, address):
        self.router = Router(address)
        self.public_key = None
        self.shared_keys = {}
        self.private_keys = {}

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

    async def send_public_key(self, dst_addr):
        self.public_key, self.private_keys[dst_addr] = Kyber768.keygen()
        message = Message(
            "public_key",
            self.router.address,
            dst_addr,
            {"public_key": list(self.public_key)},
        )
        self.router.send(message)

    def send_cypher_text(self, dst_addr, ct):
        message = Message(
            "cypher_text", self.router.address, dst_addr, {"cypher_text": list(ct)}
        )
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
            if message.get_source() in self.shared_keys:
                cypher = AESCipher(self.shared_keys[message.get_source()])
                message_decoded = cypher.decrypt(text)
                return (
                    f"Encrypted message {text}\n"
                    f"Decrypted message from {message.get_source()}: {message_decoded}"
                )
            else:
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

        elif message.get_command() == "public_key":
            cypher_text, shared_key = Kyber768.enc(
                bytes(message.get_param("public_key"))
            )
            src_addr = message.get_source()
            self.shared_keys[src_addr] = shared_key
            self.send_cypher_text(src_addr, list(cypher_text))
            return f"Shared key is generated for {src_addr}"

        elif message.get_command() == "cypher_text":
            shared_key = Kyber768.dec(
                bytes(message.get_param("cypher_text")),
                self.private_keys[message.get_source()],
            )
            self.shared_keys[message.get_source()] = shared_key
            return "Shared key is decoded from cypher_text"

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
