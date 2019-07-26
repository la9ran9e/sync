import socket

from .transport import ClientSocket
from .transport import OK, BAD
from .processor import ClientProcessor


def _sock_factory(address):
    return ClientSocket(address,
                        family=socket.AF_INET,
                        type=socket.SOCK_DGRAM)


class Client:
    def __init__(self, server_address,
                 sock_factory=_sock_factory,
                 processor_factory=ClientProcessor):
        self._sock = sock_factory(server_address)
        self._processor = processor_factory()
        self._items_registry = set()

    async def _perform_command(self, command, _id):
        msg = self._processor.process(command, _id)
        await self._sock.send(msg)
        return await self._sock.wait_for_notice()

    async def acquire(self, _id):
        await self._perform_command('acquire', _id)
        self._items_registry.add(_id)

    async def release(self, _id):
        await self._perform_command('release', _id)
        self._items_registry.remove(_id)

    async def acquire_no_wait(self, _id):
        res = await self._perform_command('release', _id)
        if res == OK:
            return True
        elif res == BAD:
            return False
        else:
            raise KeyError(f"Unexpected response: {res!r}")

    async def close(self):
        items = [_ for _ in self._items_registry]
        for _id in items:
            await self.release(_id)
