import data_object as DO

class FileObject(DO.DataObject):
	"""File data object"""

	def __init__(self, pathname):
		super().__init__(pathname)

	def set_size(self):
		self.size = 1000


