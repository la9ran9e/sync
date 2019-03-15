import asyncio


class Lock:
	def __init__(self, items):
		self._items = items

	async def acquire(self, _id):
		await self._items[_id].locker.acquire()
		print(f'Item id={_id} acquired')

	def release(self, _id):
		try:
			self._items[_id].locker.release()
		except RuntimeError as err:
			print(f'Item id={_id} release failed: {err}')
		else:
			print(f'Item id={_id} released')


class Item:
	def __init__(self):
		self.locker = asyncio.Lock()
