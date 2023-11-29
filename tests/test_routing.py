from dabudimesh.network import NetworkInterfaceController
from time import sleep


def test_routing():
    output = []
    routers_num = 10
    nics = []
    for i in range(routers_num):
        nics.append(NetworkInterfaceController(output))

    for i in range(1, routers_num):
        addr = nics[i - 1].router.address
        nics[i].connect_with(addr)
        sleep(0.1)

    # Add some connections
    nics[7].connect_with(nics[2].router.address)
    nics[0].connect_with(nics[9].router.address)
    sleep(0.1)

    for i in range(routers_num):
        for j in range(routers_num):
            if i != j:
                assert nics[i].router.address in nics[j].router.available_addresses()

    msg_text = "msg text"
    src_addr = nics[3].router.address
    dst_addr = nics[7].router.address
    nics[3].send_text(dst_addr, msg_text)
    sleep(0.1)
    assert output[-1] == f"Message from {src_addr}: {msg_text}"

    for i in range(routers_num):
        nics[i].stop()
