class Error(Exception):
	"""Base class for exceptions in this module. Taken from python docs"""
	pass

class ArgumentError(Error):
	"""Exception raised for incorrect argument types, or required args that were not initialized.

	Attributes:
		msg  -- explanation of the error
	"""
	def __init__(self, msg):
		self.msg = "ArgumentError: "+msg

class AdapterError(Error):
	"""Exception raised for failures relating to the adapter dictionary provided to Automan constructor

	Attributes:
		msg  -- explanation of the error
	"""
	def __init__(self, msg):
		self.msg = "AdapterError: "+msg

class UnsupportedServerError(Error):
	"""Exception raised for using non-local servers, currently package only supports 'localhost' as valid arg

	Attributes:
		msg  -- explanation of the error
	"""
	def __init__(self):
		self.msg = 'UnsupportedServerError: Currently, PyAutoman only supports locally hosted servers at localhost'

class RPCServerError(Error):
	"""Exception raised for various server errors:
	errors:
		- unable to start rpc server process

	Attributes:
		msg  -- explanation of the error
	"""
	def __init__(self, msg):
		self.msg =  "RPCServerError: "+msg