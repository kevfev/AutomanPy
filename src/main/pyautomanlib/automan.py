import core.automanlib as pyAutomanlib
from core.automanlib_rpc_pb2 import TaskResponse
import random
import sys

class Automan():

	def __init__(self, adapter, server_addr = 'localhost', port = 50051):
		self.adptr = pyAutomanlib.make_adapter(adapter["access_id"], adapter["access_key"], sandbox_mode=adapter["sandbox_mode"]) if pyAutomanlib.isGoodAadapter(adapter) else None
		self.srvr_addr = server_addr
		self.port = port
		self.channel = self.init_channel(server_addr, port)

		if self.adptr is None:
			sys.exit("Invalid adapter, check parameters used")

		# set up channel, connect to gRPC server, register adapter credentials with server
		self.stub = self.init_channel(server_addr, port)
		pyAutomanlib.register_adapter_to_server(self.channel, self.adptr)




	def shutdown(self):
		pyAutomanlib.shutdown_rpc_server(self.channel)

	def init_channel(self, server_addr, port):
		self.channel = pyAutomanlib.make_channel(server_addr,str(port))

	def estimate(self, text, budget, title, image_url, include_rand_in_title = True):
		task = pyAutomanlib.make_est_task(text_ = text,
	    								budget_ = budget,
	    								title_ = title,
	    								image_url_ = "https://docs.google.com/uc?id=1ZQ-oL8qFt2tx_T_-thev2O4dsugVbKI2")
		resp = pyAutomanlib.submit_task(self.channel, task)
		outcome = self.handleResponse(resp)

		return outcome
