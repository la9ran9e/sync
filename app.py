import socket
import collections

from sync import locker, transport, processor, server
import settings


def main(): 
	sock = transport.ServerSocket(settings.SERVER_ADDR, socket.AF_INET, socket.SOCK_DGRAM)
	proc = processor.Processor()
	items = collections.defaultdict(locker.Item)
	lock = locker.Lock(items)

	server_app = server.Server(sock, proc, lock)
	server_app.run()

if __name__ == '__main__':
	main()