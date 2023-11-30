from network import NetworkInterfaceController
from shell import DabudiShell
from time import sleep


def test_shell():
    output1 = []
    output2 = []
    nic1 = NetworkInterfaceController(output1)
    nic2 = NetworkInterfaceController(output2)
    shell = DabudiShell(nic1)

    addr1 = nic1.router.address
    addr2 = nic2.router.address

    shell.onecmd("connect " + addr2)
    sleep(0.01)
    assert addr1 in nic2.router.neighbors
    assert addr1 in nic2.router.available_addresses()
    assert addr2 in nic1.router.neighbors
    assert addr2 in nic1.router.available_addresses()
    assert output2[-1] == f"Accepted connection from {addr1}"

    msg_test = "msg to second"
    shell.onecmd("message " + addr2 + " " + msg_test)
    sleep(0.1)
    assert output2[-1] == f"Message from {addr1}: {msg_test}"

    shell.onecmd("exit")
    nic2.stop()
