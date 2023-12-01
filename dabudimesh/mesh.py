from network import NetworkInterfaceController
from utils import create_server, socket_address, run_event_loop
from config import MAX_TIME_WAIT
import asyncio
from threading import Thread


# TODO: replace output list with logger
class MeshNetworkNode:
    def __init__(self, output: list):
        self.output = output
        listener = create_server()
        address = socket_address(listener)
        self.nic = NetworkInterfaceController(address)

        self.event_loop = asyncio.new_event_loop()
        self.event_loop.add_reader(listener, self.__on_accept, listener)
        thread = Thread(target=run_event_loop, args=(self.event_loop,))
        thread.start()

    def stop(self):
        # TODO: inform neighbors
        self.event_loop.call_soon_threadsafe(self.event_loop.stop)

    def get_routing_table(self):
        return self.nic.router.routing_table

    def get_neighbour_addresses(self):
        return self.nic.router.neighbors.keys()

    def get_address(self):
        return self.nic.router.address

    def get_available_addresses(self):
        return self.nic.router.available_addresses()

    def connect_with(self, addr):
        if addr == self.get_address():
            return False

        fut = asyncio.run_coroutine_threadsafe(
            self.nic.connect_with(addr), self.event_loop
        )
        sock = fut.result(MAX_TIME_WAIT)

        if sock is None:
            return False

        self.event_loop.call_soon_threadsafe(
            self.event_loop.add_reader, sock, self.__on_read, addr
        )
        return True

    def send_text(self, dst_addr, text):
        fut = asyncio.run_coroutine_threadsafe(
            self.nic.send_text(dst_addr, text), self.event_loop
        )
        fut.result(MAX_TIME_WAIT)

        return True

    def __on_read(self, address):
        try:
            output = self.nic.handle_message(address)
            if output is not None:
                self.output.append(output)

        except Exception:
            self.output.append(f"Router {address} disconnected")
            self.stop(self)
            exit()

    def __on_accept(self, server):
        (neighbor, neighbor_address) = self.nic.accept_connection(server)

        asyncio.get_event_loop().add_reader(neighbor, self.__on_read, neighbor_address)
        self.output.append(f"Accepted connection from {neighbor_address}")
