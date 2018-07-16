from automanlib_rpc_pb2 import *
from automanlib_classes_pb2 import *
import automanlib_rpc_pb2_grpc
import grpc

def isGoodAadapter(adapter):
	required_strings = ["access_id", "access_key", "type"]
	for req in required_strings:
		if req not in adapter:
			print("ERROR: Required paramater missing in adapter. Adapter needs access_id id, access_key, and adapter type")
			return False
	return True

def _make_client_stub(channel_):
	return automanlib_rpc_pb2_grpc.EstimationPrototypeStub(channel_)

def make_adapter(acc_id, acc_key, **kwargs):
	adptr = AdapterCredentials(adptr_type = AdapterCredentials.MTURK, access_id = acc_id, access_key = acc_key, adapter_options = kwargs )
	return adptr


def make_channel(address_, port_):
	#assert strings here, type check, error check, throw exceptions
	channel = grpc.insecure_channel(address_+":"+port_)
	return channel

def make_est_task(title_, text_, image_url_, budget_):
	return make_task(task_type_ =Task.ESTIMATE, tit=title_ ,txt=text_, image_url = image_url_, budg=budget_)

def make_task(task_type_, tit, txt, image_url, budg):
	#consider using a task builder classs to make tasks in this method
	return Task(task_type=task_type_, title=tit ,text=txt, img_url = image_url, budget=budg)

def submit_task(channel_,task_):
	#assert channel here, type check, error check, throw exceptions
	_at_task = AutomanTask(request = task_)
	client_stub = _make_client_stub(channel_)
	response = client_stub.SubmitTask(_at_task)
	return response

def shutdown_rpc_server(channel_):
	client_stub = _make_client_stub(channel_)
	stat_resp = client_stub.KillServer(Empty())
	return stat_resp


def get_server_status():
	pass

def register_adapter_to_server(channel_, adptr):
	client_stub = _make_client_stub(channel_)
	response = client_stub.RegisterAdapter(adptr)
	return response


def handleResponse(self,response):
	ret_string = None
	if response.return_code == TaskResponse.VALID:
		return response.outcome
	if response.return_code == TaskResponse.UNDEFINED_RESP_CODE:
		ret_string= "ERROR: An undefind response code was returned. Application may be out of data or there is an error on the grpc server side"
	if response.return_code == TaskResponse.ERROR:
		ret_string = "ERROR: An error occured \n"+ "Message: "+response.err_msg
	if response.return_code == TaskResponse.EXCEPTION:
		ret_string ="EXCEPTION: An exception occured \n"+ "Message: "+response.excep_msg

	sys.exit(ret_string)