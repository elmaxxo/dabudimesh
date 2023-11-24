import pydbus
import random
import socket


DEFAULT_BLUETOOTH_PORT = 54321


def getMAC():
    bus = pydbus.SystemBus()
    adapter = bus.get("org.bluez", "/org/bluez/hci0")
    return adapter.Address


def create_tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", random.randint(1000, 5000)))
    s.listen()
    return s


def create_tcp_connection(addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", int(addr)))
    return s


def create_bluetooth_server():
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.bind((getMAC(), DEFAULT_BLUETOOTH_PORT))
    s.listen()
    return s


def create_bluetooth_connection(addr):
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect((addr, DEFAULT_BLUETOOTH_PORT))
    return s


def create_server(is_bluetooth=False):
    return create_bluetooth_server() if is_bluetooth else create_tcp_server()


def create_connection(addr, is_bluetooth=False):
    return (
        create_bluetooth_connection(addr)
        if is_bluetooth
        else create_tcp_connection(addr)
    )


def socket_address(sock, is_bluetooth=False):
    sock_addr = sock.getsockname()
    return str(sock_addr[0] if is_bluetooth else sock_addr[1])
