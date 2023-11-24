from dabudimesh.router import Router
from dabudimesh.utils import create_tcp_server, socket_address, create_tcp_connection


def test_direct():
    l1, l2 = create_tcp_server(), create_tcp_server()
    p1, p2 = socket_address(l1), socket_address(l2)
    r1, r2 = Router(p1, l1), Router(p2, l2)

    s1 = create_tcp_connection(p2)
    r1.add_connection(p2, s1)

    (s2, p1_2) = r2.accept()

    r1.send_message(p2, "Hello from R1!")
    received = r2.process_message_from(s2)
    assert received == "Hello from R1!"

    r2.send_message(p1_2, "Hello from R2!")
    received = r1.process_message_from(s1)
    assert received == "Hello from R2!"
