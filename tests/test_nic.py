from dabudimesh.network import NetworkInterfaceController
from time import sleep


def test_nic():
    output1 = []
    output2 = []
    nic1 = NetworkInterfaceController(output1)
    nic2 = NetworkInterfaceController(output2)

    addr1 = nic1.router.address
    addr2 = nic2.router.address

    nic1.connect_with(addr2)
    sleep(0.01)
    assert addr1 in nic2.router.neighbors
    assert addr1 in nic2.router.available_addresses()
    assert addr2 in nic1.router.neighbors
    assert addr2 in nic1.router.available_addresses()
    assert output2[-1] == f"Accepted connection from {addr1}"

    msg_test = "msg to first"
    nic2.send_text(addr1, msg_test)
    sleep(0.1)
    assert output1[-1] == f"Message from {addr2}: {msg_test}"

    nic1.stop()
    nic2.stop()
