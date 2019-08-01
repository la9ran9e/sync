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

    def _perform_command(self, command, _id):
        msg = self._processor.process(command, _id)
        self._sock.send(msg)
        return self._sock.wait_for_notice()

    def acquire(self, _id):
        self._perform_command('acquire', _id)
        self._items_registry.add(_id)

    def release(self, _id):
        self._perform_command('release', _id)
        self._items_registry.remove(_id)

    def acquire_no_wait(self, _id):
        res = self._perform_command('acquire_no_wait', _id)
        if res == OK:
            self._items_registry.add(_id)
            return True
        elif res == BAD:
            return False
        else:
            raise KeyError(f"Unexpected response: {res!r}")

    def close(self):
        items = [_ for _ in self._items_registry]
        for _id in items:
            self.release(_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
