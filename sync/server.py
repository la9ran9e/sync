import socket
import asyncio

from .processor import Processor, ProcessError
from .transport import ServerSocket
from .locker import Lock


def _sock_factory(address):
    return ServerSocket(address,
                        family=socket.AF_INET,
                        type=socket.SOCK_DGRAM)


class Server:
    def __init__(self, bind_address,
                 sock_factory=_sock_factory,
                 processor_factory=Processor,
                 locker_factory=Lock,
                 loop=None):
        self._sock = sock_factory(bind_address)
        self._processor = processor_factory()
        self._locker = locker_factory()
        self._loop = loop if loop else asyncio.get_event_loop()

    def run(self):
        self._loop.run_until_complete(self._do_run())

    async def _do_run(self):
        await self._listen()

    async def _listen(self):
        while True:
            msg, address = await self._sock.getone()
            try:
                command, _id = self._processor.process(msg)
            except ProcessError as err:
                print(err)
                await self._sock.notice_error(address, err)
                continue

            try:
                self._loop.create_task(self._handle_command(command, _id, address))
            except Exception as err:
                await self._sock.notice_error(address, err)

    async def _handle_command(self, command, _id, address):
        if command == 'acquire':
            await self._locker.acquire(_id)
            await self._sock.notify(address)
        elif command == 'release':
            self._locker.release(_id)
            await self._sock.notify(address)
        elif command == 'acquire_no_wait':
            ok = await self._locker.acquire_no_wait(_id)
            await self._sock.notify(address, ok=ok)
