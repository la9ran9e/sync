import socket
import asyncio


class AIOSocket:
    def __init__(self, family, type, loop=None):
        self._loop = loop or asyncio.get_event_loop()

        self._sock = socket.socket(family, type, 0)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setblocking(False)

    def recvfrom(self, n_bytes, fut=None, registed=False):
        fd = self._sock.fileno()
        if fut is None:
            fut = self._loop.create_future()
        if registed:
            self._loop.remove_reader(fd)

        try:
            data, addr = self._sock.recvfrom(n_bytes)
        except (BlockingIOError, InterruptedError):
            self._loop.add_reader(fd, self.recvfrom, n_bytes, fut, True)
        else:
            fut.set_result((data, addr))
        return fut

    def sendto(self, data, addr, fut=None, registed=False):
        fd = self._sock.fileno()
        if fut is None:
            fut = self._loop.create_future()
        if registed:
            self._loop.remove_writer(fd)
        if not data:
            return

        try:
            n = self._sock.sendto(data, addr)
        except (BlockingIOError, InterruptedError):
            self._loop.add_writer(fd, self.sendto, data, addr, fut, True)
        else:
            fut.set_result(n)
        return fut

    def __getattr__(self, attr):
        return getattr(self._sock, attr)


OK = bytes('1', encoding='UTF-8')
BAD = bytes('0', encoding='UTF-8')
ERROR = bytes('e', encoding='UTF-8')


class ServerSocket:
    def __init__(self, address, family, type):
        self._loop = asyncio.get_event_loop()
        self._sock = AIOSocket(family, type)
        self._sock.bind(address)

    async def getone(self):
        msg, address = await self._sock.recvfrom(1024)
        return msg.decode('UTF-8').rstrip(), address

    async def notify(self, address, ok=True):
        await self._sock.sendto(OK if ok else BAD, address)

    async def notice_error(self, address):
        await self._sock.sendto(ERROR, address)


class ClientSocket:
    def __init__(self, address, family, type):
        self._address = address
        self._sock = socket.socket(family, type)

    def send(self, msg):
        body = bytes(msg, encoding='UTF-8')
        self._sock.sendto(body, self._address)

    def wait_for_notice(self):
        while True:
            resp, addr = self._sock.recvfrom(1)
            if addr == self._address:
                return resp
            else:
                print(f'message from unexpected address: {addr}')
