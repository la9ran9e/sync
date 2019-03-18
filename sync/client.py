class Client:
	def __init__(self, sock, processor):
		self._sock = sock
		self._processor = processor

	async def _perform_command(self, command, _id):
		msg = self._processor.process(command, _id)
		await self._sock.send(msg)
		await self._sock.wait_for_notice()

	async def acquire(self, _id):
		await self._perform_command('acquire', _id)

	async def release(self, _id):
		await self._perform_command('release', _id)
