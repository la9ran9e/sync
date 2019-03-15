import asyncio
from sync import processor


class Server:
	def __init__(self, sock, processor, locker, workers=100):
		self._sock = sock
		self._processor = processor
		self._locker = locker
		self._loop = asyncio.get_event_loop()
		self._queue = asyncio.Queue(maxsize=workers)
		self._workers_num = workers

	def run(self):
		self._loop.run_until_complete(self._do_run())

	async def _do_run(self):
		self._worker_tasks = [self._loop.create_task(self._worker(_id)) for _id in range(self._workers_num)]
		self._listen_task = self._loop.create_task(self._listen())
		await asyncio.wait([*self._worker_tasks, self._listen_task])

	async def _listen(self):
		while True:
			msg, address = await self._sock.getone()
			try:
				command, _id = self._processor.process(msg)
			except processor.ProcessError as err:
				print(err)
				continue

			await self._queue.put((command, _id, address))

	async def _worker(self, _id):
		while True:
			command, _id, address = await self._queue.get()
			if command == 'acquire':
				await self._locker.acquire(_id)
				await self._sock.notify(address)
			else:
				self._locker.release(_id)
				await self._sock.notify(address)

			self._queue.task_done()
