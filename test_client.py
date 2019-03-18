import socket
import asyncio

from sync import transport, processor, client
import settings

async def proc1():
	sock = transport.ClientSocket(settings.SERVER_ADDR, socket.AF_INET, socket.SOCK_DGRAM)
	proc = processor.ClientProcessor()

	client_app = client.Client(sock, proc)

	await client_app.acquire(1)
	print('proc1 locked item id=1')
	await asyncio.sleep(1)
	await client_app.release(1)
	print('proc1 released item id=1')

async def proc2():
	sock = transport.ClientSocket(settings.SERVER_ADDR, socket.AF_INET, socket.SOCK_DGRAM)
	proc = processor.ClientProcessor()

	client_app = client.Client(sock, proc)

	await asyncio.sleep(.1)
	print('proc2 waiting for item id=1')
	await client_app.acquire(1)
	print('proc2 locked item id=1')
	await client_app.release(1)
	print('proc2 released item id=1')


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	tasks = asyncio.gather(proc1(), proc2())
	try:
		loop.run_until_complete(tasks)
	finally:
		loop.close()

