from dabudimesh.mesh import MeshNetworkNode
from shell import DabudiShell
from time import sleep


def test_shell():
    output1 = []
    output2 = []
    node1 = MeshNetworkNode(output1)
    node2 = MeshNetworkNode(output2)
    shell = DabudiShell(node1)

    addr1 = node1.get_address()
    addr2 = node2.get_address()

    shell.onecmd("connect " + addr2)
    sleep(0.1)
    assert addr1 in node2.get_neighbour_addresses()
    assert addr1 in node2.get_available_addresses()
    assert addr2 in node1.get_neighbour_addresses()
    assert addr2 in node1.get_available_addresses()
    assert output2[-1] == f"Accepted connection from {addr1}"

    msg_test = "msg to second"
    shell.onecmd("message " + addr2 + " " + msg_test)
    sleep(0.1)
    assert output2[-1] == f"Message from {addr1}: {msg_test}"

    assert shell.onecmd("exit")
    node2.stop()
