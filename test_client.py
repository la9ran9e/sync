import asyncio

from sync import Client
import settings


async def proc1():
	client_app = Client(settings.SERVER_ADDR)

	await client_app.acquire(1)
	print('proc1 locked item id=1')
	await asyncio.sleep(1)
	await client_app.release(1)
	print('proc1 released item id=1')


async def proc2():
	client_app = Client(settings.SERVER_ADDR)

	await asyncio.sleep(.1)
	print('proc2 waiting for item id=1')
	try:
		await asyncio.wait_for(client_app.acquire(1), timeout=.1)
	except asyncio.TimeoutError:
		print("timeout expired")
		await client_app.close()
		
	# 	await client_app.release(1)
	# 	print('proc2 released item id=1')

	# print('proc2 locked item id=1')


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	tasks = asyncio.gather(proc1(), proc2())
	try:
		loop.run_until_complete(tasks)
	finally:
		loop.close()
