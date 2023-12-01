from router import Router
from utils import create_server, create_connection, socket_address
from message import Message
from utils import run_event_loop
from config import MSG_MAX_LEN
import asyncio
from threading import Thread
from cyphers.kyber  import  Kyber768
from cyphers.aescypher import AESCipher

# TODO: replace output list with logger
class NetworkInterfaceController:
    def __init__(self, output: list):
        self.output = output
        self.public_key = None
        self.shared_keys={}
        self.private_keys={}
        listener = create_server()
        address = socket_address(listener)
        self.router = Router(address)
        self.event_loop = asyncio.new_event_loop()
        self.event_loop.add_reader(listener, self.__on_accept, listener)
        thread = Thread(target=run_event_loop, args=(self.event_loop,))
        thread.start()

    def stop(self):
        # TODO: inform neighbors
        self.event_loop.call_soon_threadsafe(self.event_loop.stop)

    def connect_with(self, addr):
        sock = create_connection(addr)
        if sock is None:
            return False

        greeting = Message("greeting", self.router.address, addr)
        sock.sendall(greeting.encode())

        public_key, private_key = Kyber768.keygen()
        self.private_keys[addr] = private_key
        self.public_key = public_key
        
        message = Message.decode(sock.recv(MSG_MAX_LEN))
        assert message.get_command() == "routes"
        addr_to = message.get_source()
        routing_table = message.get_param("routing_table")
        self.router.add_routes(addr_to, routing_table.keys())

        self.broadcast_route(addr)
        self.router.add_neighbor(addr, sock)
        self.send_routes_to(addr)

        self.event_loop.call_soon_threadsafe(
            self.event_loop.add_reader, sock, self.__on_read, addr
        )
        return True
    def send_public_key(self,dst_addr,pk):
        message = Message("public_key", self.router.address, dst_addr, {"public_key": list(pk)})
        self.router.send(message)
        print("Public key is sended")

    def send_cypher_text(self,dst_addr,st):
        message = Message("cypher_text", self.router.address, dst_addr, {"cypher_text": list(st)})
        self.router.send(message)
        print("Cypher text is sended")
        
    def send_text(self, dst_addr, text):
        
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

    def __on_read(self, address):
        try:
            message = self.router.route_pending()
            if message is None:
                return
            if message.get_command() == "text":
                text = message.get_param("text")
                if message.get_source() in self.shared_keys:
                    cypher = AESCipher(self.shared_keys[message.get_source()])
                    print(self.shared_keys[message.get_source()])
                    message_decoded=cypher.decrypt(text).decode("utf-8")
                    self.output.append(f"Decrypted message from {message.get_source()}: {message_decoded}")
                else:
                    self.output.append(f"Message from {message.get_source()}: {text}")
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
                cypher_text, shared_key = Kyber768.enc(bytes(message.get_param("public_key")))
                print("Shared key is generated")
                self.shared_keys[message.get_source()] = shared_key
                self.send_cypher_text(message.get_source(),list(cypher_text))

            elif message.get_command() == "cypher_text":
                shared_key = Kyber768.dec(bytes(message.get_param("cypher_text")), self.private_keys[message.get_source()])
                self.shared_keys[message.get_source()] = shared_key
                print("Shared key is decoded from cypher_text")

            else:
                self.output.append(f"Can't handle command: {message.get_command()}")

        except Exception:
            self.output.append(f"Router {address} disconnected")
            self.stop(self)
            exit()

    def __on_accept(self, server):
        neighbor = server.accept()[0]
        message = Message.decode(neighbor.recv(MSG_MAX_LEN))
        assert message.get_command() == "greeting"
        neighbor_address = message.get_source()

        self.broadcast_route(neighbor_address)
        self.router.add_neighbor(neighbor_address, neighbor)
        self.send_routes_to(neighbor_address)

        asyncio.get_event_loop().add_reader(neighbor, self.__on_read, neighbor_address)
        self.output.append(f"Accepted connection from {neighbor_address}")
