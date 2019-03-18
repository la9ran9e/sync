class ProcessError(Exception): pass


class Processor:
	def process(self, msg):
		result = msg.split(' ')
		if len(result) != 2:
			raise ProcessError('result length not eq 2')
		command, id = result
		if command not in frozenset(['acquire', 'release']):
			raise ProcessError(f'Wrong command {command}')

		return command, id


class ClientProcessor:
	def process(self, command, _id):
		msg = f'{command} {_id}'
		return msg
