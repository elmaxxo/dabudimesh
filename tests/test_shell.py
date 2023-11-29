from dabudimesh.router import Router
from shell import DabudiShell
from utils import create_tcp_server
from dabudimesh.message import Message


def test_shell():
    p1, p2 = str(1599), str(3210)
    serv2 = create_tcp_server(p2)
    r1, r2 = Router(p1), Router(p2)

    shell = DabudiShell(r1, None)

    shell.onecmd("connect " + p2)

    neighbor = serv2.accept()[0]
    greeting = Message.decode(neighbor.recv(1337))
    assert greeting.get_command() == "greeting"
    r2.add_neighbor(greeting.get_source(), neighbor)

    assert p2 in r1.routing_table
    assert p1 in r2.routing_table

    text = "msg to R2"
    shell.onecmd("message " + p2 + " " + text)
    received = r2.route_pending()
    assert received.get_command() == "text"
    assert received.get_params()["text"] == text

    assert shell.onecmd("exit")
