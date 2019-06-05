

class DataObject(object):
	"""Abstract class that wraps a file object"""

	def __init__(self, pathname):
		self.pathname = pathname
		self.set_size()

	def set_pathname(self, pathname):
		self.pathname = pathname

	def set_size(self):
		raise NotImplementedError()

