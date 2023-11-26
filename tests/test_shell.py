from dabudimesh.router import Router
from shell import DabudiShell
from utils import create_tcp_server, socket_address


def test_shell():
    l1, l2 = create_tcp_server(), create_tcp_server()
    p1, p2 = socket_address(l1), socket_address(l2)
    r1, r2 = Router(p1, l1), Router(p2, l2)

    shell = DabudiShell(r1, None)

    shell.onecmd("connect " + p2)
    (s2, p1_2) = r2.accept()

    assert p2 in r1.routing_table
    assert p1 in r2.routing_table

    sended = "msg to R2"
    shell.onecmd("message " + p2 + " " + sended)
    recieved = r2.process_message_from(s2)
    assert recieved == sended

    assert shell.onecmd("exit")
