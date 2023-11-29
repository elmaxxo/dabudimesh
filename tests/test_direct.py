from dabudimesh.router import Router
from dabudimesh.utils import create_tcp_server, create_tcp_connection, socket_address
from dabudimesh.message import Message


def test_direct():
    p1 = str(1500)
    serv2 = create_tcp_server()
    p2 = socket_address(serv2)
    r1, r2 = Router(p1), Router(p2)

    s1 = create_tcp_connection(p2)
    r1.add_neighbor(p2, s1)
    s2 = serv2.accept()[0]
    # r2 will get the address from a greeting message
    r2.add_neighbor(p1, s2)

    message_sent = Message("any", p1, p2)
    r1.send(message_sent)
    message_received = r2.route_pending()
    assert message_sent.fields == message_received.fields

    message_sent = Message("special", p2, p1)
    r2.send(message_sent)
    message_received = r1.route_pending()
    assert message_sent.fields == message_received.fields
