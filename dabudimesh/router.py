from message import read_message
from select import select


class Router:
    def __init__(self, address):
        self.routing_table = {}
        self.neighbors = {}
        self.address = address

    def available_addresses(self):
        return self.routing_table.keys()

    def add_neighbor(self, address, socket):
        self.neighbors[address] = socket
        self.routing_table[address] = address

    def add_route(self, addr_from, addr_to):
        if addr_from not in self.available_addresses():
            self.routing_table[addr_from] = addr_to

    def add_routes(self, addr_to, new_addresses):
        for addr_from in new_addresses:
            if addr_from != self.address:
                self.add_route(addr_from, addr_to)

    def send(self, message):
        neighbor_addr = self.routing_table[message.get_destination()]
        neighbor = self.neighbors[neighbor_addr]
        neighbor.sendall(message.encode())

    def route_pending(self):
        ready_neighbors, _, _ = select(self.neighbors.values(), [], [], 0)
        if len(ready_neighbors) == 0:
            return None

        for neighbor in ready_neighbors:
            message = read_message(neighbor)
            destination = message.get_destination()

            print(f"Recieved message: {message.fields}")
            if destination == self.address:
                return message
            else:
                print(f"Forward message: {message.fields}")
                self.send(message)
        return None
