from router import Router
from shell import DabudiShell
import asyncio
import random


def main():
    address = str(random.randint(1500, 5000))
    router = Router(address)

    loop = asyncio.new_event_loop()
    shell = DabudiShell(router, loop)
    loop.run_in_executor(None, shell.cmdloop)
    loop.run_forever()


if __name__ == "__main__":
    main()
