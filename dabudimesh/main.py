from network import NetworkInterfaceController
from shell import DabudiShell


def main():
    nic_output = []
    nic = NetworkInterfaceController(nic_output)
    shell = DabudiShell(nic, nic_output)
    shell.cmdloop()


if __name__ == "__main__":
    main()
