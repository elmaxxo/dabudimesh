from dabudimesh.mesh import MeshNetworkNode
from time import sleep


def test_routing():
    output = []
    routers_num = 10
    nodes = []
    for i in range(routers_num):
        nodes.append(MeshNetworkNode(output))

    for i in range(1, routers_num):
        addr = nodes[i - 1].get_address()
        assert nodes[i].connect_with(addr)
        sleep(0.1)

    # Add some connections
    nodes[3].connect_with(nodes[8].get_address())
    nodes[7].connect_with(nodes[2].get_address())
    nodes[0].connect_with(nodes[9].get_address())
    sleep(0.1)

    for i in range(routers_num):
        for j in range(routers_num):
            if i != j:
                assert nodes[i].get_address() in nodes[j].get_available_addresses()

    msg_text = "msg text"
    src_addr = nodes[3].get_address()
    dst_addr = nodes[7].get_address()
    assert nodes[3].send_text(dst_addr, msg_text)
    sleep(0.1)
    assert output[-1] == f"Message from {src_addr}: {msg_text}"

    for i in range(routers_num):
        nodes[i].stop()
