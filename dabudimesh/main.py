from mesh import MeshNetworkNode
from shell import DabudiShell


def main():
    node_output = []
    node = MeshNetworkNode(node_output)
    shell = DabudiShell(node, node_output)
    shell.cmdloop()


if __name__ == "__main__":
    main()
