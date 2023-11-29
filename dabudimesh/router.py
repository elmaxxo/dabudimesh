# from email import message
from message import Message
from select import select

MSG_MAX_LEN = 4096


class Router:
    def __init__(self, address):
        self.routing_table = {}
        self.neighbors = {}
        self.address = address

    def add_neighbor(self, address, socket):
        self.neighbors[address] = socket
        self.routing_table[address] = address

    def add_route(self, addr_from, addr_to):
        self.routing_table[addr_from] = addr_to

    def send(self, message):
        neighbor_addr = self.routing_table[message.get_destination()]
        neighbor = self.neighbors[neighbor_addr]
        neighbor.sendall(message.encode())

    def route_pending(self):
        ready_neighbors, _, _ = select(self.neighbors.values(), [], [], 0)
        if len(ready_neighbors) == 0:
            return None

        assert len(ready_neighbors) == 1
        # TODO: handle len(ready_neighbors) >= 1
        neighbor = ready_neighbors[0]
        message = Message.decode(neighbor.recv(MSG_MAX_LEN))
        destination = message.get_destination()
        if destination == self.address:
            return message
        else:
            self.send(message)
            return None
