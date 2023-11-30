from dabudimesh.message import Message
from dabudimesh.utils import create_tcp_server, socket_address, create_connection
from dabudimesh.router import Router


def test_encoding_message():
    msg = Message("message", "1000", "2000", {"text": "Message to 2000"})

    assert Message.decode(msg.encode()).fields == msg.fields


def test_sending_message():
    p1 = str(1599)
    serv2 = create_tcp_server()
    p2 = socket_address(serv2)
    r1, r2 = Router(p1), Router(p2)

    sock = create_connection(p2)
    greeting = Message("greeting", p1, p2)
    sock.sendall(greeting.encode())
    r1.add_neighbor(p2, sock)

    neighbor = serv2.accept()[0]
    greeting = Message.decode(neighbor.recv(1337))
    assert greeting.get_command() == "greeting"
    r2.add_neighbor(greeting.get_source(), neighbor)

    assert p2 in r1.routing_table
    assert p1 in r2.routing_table

    text = "msg to R2"
    message = Message("text", p1, p2, {"text": text})
    sock.sendall(message.encode())

    received = r2.route_pending()
    assert received.get_command() == "text"
    assert received.get_params()["text"] == text
