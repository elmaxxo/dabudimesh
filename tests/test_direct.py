from dabudimesh.router import Router
from socket import create_server, create_connection


def test_direct():
    p1, p2 = 1486, 1487
    l1, l2 = create_server(("localhost", p1)), create_server(("localhost", p2))
    r1, r2 = Router(p1, l1), Router(p2, l2)

    s1 = create_connection(("localhost", p2))
    r1.add_connection(p2, s1)

    (s2, p1_2) = r2.accept()

    r1.send(p2, "Hello from R1!")
    received = r2.process_message_from(s2)
    assert received == "Hello from R1!"

    r2.send(p1_2, "Hello form R2!")
    received = r1.process_message_from(s1)
    # TODO: R1 drops the message because p1_2 != p1,
    #       so we should use something different from ports for addresses
    assert received == "Hello from R2!"
