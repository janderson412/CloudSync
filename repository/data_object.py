

class DataObject(object):
	"""Abstract class that wraps a file object"""

	def __init__(self, pathname):
		self.pathname = pathname
		self.get_size()

	def get_size(self):
		self.size = 0
