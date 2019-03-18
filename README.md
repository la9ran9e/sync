# sync
A distributed synchronization service.

## Starting

```bash
python3.6 app.py
```

After server started listening:
```bash
nc -u 127.0.0.1 10000
acquire 1
acquire 2
release 2
release 1
```

## Client

```python
# test_client.py

import socket
import asyncio
import collections

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

# result log:

# proc1 locked item id=1
# proc2 waiting for item id=1
# proc1 released item id=1
# proc2 locked item id=1
# proc2 released item id=1

```
