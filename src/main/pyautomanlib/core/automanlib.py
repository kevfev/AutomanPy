from automanlib_rpc_pb2 import *
from automanlib_classes_pb2 import *
from automanlib_wrappers_pb2 import *
import automanlib_rpc_pb2_grpc
import grpc

def isGoodAadapter(adapter):
	"""
	Checks an adapter dictionary to ensure that it is valid. To be valid, the dictionary
	must include entries for the following keys:
		access_id - the access ID for the respective crowdsource back-end
		access_key - the secret key for the respective crowdsource back-end
		type - adapter type, determined by back-end crowdsource service

	Parameters
    ----------
    adapter : dict
    	A dictionary containing the parameters for the adapter

    Returns
    -------
    bool
    	True if the adapter validates (not authenticates) successfully
    	False otherwise
	"""

	required_strings = ["access_id", "access_key", "type"]
	for req in required_strings:
		if req not in adapter:
			print("ERROR: Required paramater missing in adapter. Adapter needs access_id id, access_key, and adapter type")
			return False
	return True

def _make_client_stub(channel_):
	"""
	Makes a gRPC client stub from the provided channel

	Parameters
    ----------
    channel_ : Channel
    	A gRPC channel

    Returns
    -------
    io.grpc.stub
    	a gRPC client stub

	"""  

	return automanlib_rpc_pb2_grpc.EstimationPrototypeStub(channel_)

def make_adapter(acc_id, acc_key, **kwargs):
	"""
	Makes an adapter from the provided parameter credentials

	Parameters
	----------
	acc_id : str
		access_id - the access ID for the respective crowdsource back-end
	acc_key : str
		access_key - the secret key for the respective crowdsource back-end
	**kwargs : dict
		a dictionary of options associated with the adapter (e.g, sandbox_mode for MTURK adapters)


	Returns
	-------
	AdapterCredentials
		an adapter object for authenticating to the crowdsource back-end
	"""

	adptr = AdapterCredentials(adptr_type = AdapterCredentials.MTURK, access_id = acc_id, access_key = acc_key, adapter_options = kwargs )
	return adptr


def make_channel(address_, port_):
	"""
	Makes a gRPC channel to communicate with server

	Parameters
	----------
	address_ : str
		The hostname of the gRPC server
	port_ : str
		The port of the gRPC server
	Returns
	-------
	Channel
    	A gRPC channel to the specified gRPC server
	"""

	#assert strings here, type check, error check, throw exceptions
	channel = grpc.insecure_channel(address_+":"+port_)
	return channel

def make_est_task(text_, image_url_, budget_, img_alt_txt_ = None, title_ = None, confidence_ = None,
				sample_size_ = -1, dont_reject_ = False, pay_all_on_failure_ = True, dry_run_ = False, 
				wage_ = None, max_value_ = None, min_value_ = None, question_timeout_multiplier_ = None, 
				initial_worker_timeout_in_s_ = None):
	"""
	Makes an estimation task for an Automan object to service

	Parameters
	----------
	title_ : str
		The title for the task, to display to workers on the crowdsource platform
	text_ : str
		The text description of the task, to display to workers on the crowdsource platform
	image_url_ : str
		The url of the image for the task
	budget_ : double
		The total budget allocated for this task

	Returns
	-------
	Task 
		A Task object initialized to the supplied parameters
	------
	"""
	task = make_task(text_=text_, image_url_=image_url_, budget_=budget_, img_alt_txt_=img_alt_txt_ , title_=title_ , 
						confidence_=confidence_ ,sample_size_=sample_size_ , dont_reject_ =dont_reject_ , 
						pay_all_on_failure_ =pay_all_on_failure_  , dry_run_ = dry_run_ , wage_ = wage_, 
						max_value_ = max_value_ , min_value_ = min_value_ , 
						question_timeout_multiplier_ = question_timeout_multiplier_ , 
						initial_worker_timeout_in_s_ initial_worker_timeout_in_s) 

	return EstimateTask(task)

def make_task(text_, image_url_, budget_, img_alt_txt_ = None, title_ = None, pattern_ = None, confidence_ = None,
				sample_size_ = -1, options_ = None, dimensions_ = None, dont_reject_ = False, pay_all_on_failure_ = True,
				dry_run_ = False, allow_empty_pattern_ = False, pattern_error_text_ = None, wage_ = None, max_value_ = None,
				min_value_ = None, question_timeout_multiplier_ = None, initial_worker_timeout_in_s_ = None):
	"""
	A general function for making tasks, used by other functions in this library for making specific tasks

	Parameters
	----------
	title_ : str
		The title for the task, to display to workers on the crowdsource platform
	text_ : str
		The text description of the task, to display to workers on the crowdsource platform
	image_url_ : str
		The url of the image for the task
	budget_ : double
		The total budget allocated for this task
	img_alt_txt_ : str
		The alternate text description for the image, for browser use
	pattern_ : str 
		The expected pattern (Freetext tasks only)
	confidence_ : double 
		The desired confidence level of the estimation		
	sample_size_ : int 
		The desired sample size for the task
	options_ : List(str)
		The option choices for radio and checkbox type tasks 
	dimensions_ : List(Dimensions)
		The dimensions to estimate (Multi-Estimate tasks only) 
	dont_reject_ : bool
		? 
	pay_all_on_failure_ : bool
		?
	dry_run_ : bool
		? 
	allow_empty_pattern_ : bool
		?
	pattern_error_text_ = str 
		The error message to display if worker response does not match expected pattern (Freetext tasks only)
	wage_ : double
		? 
	max_value_: double
		? 
	min_value : double
		? 
	question_timeout_multiplier_ : : double
		? 
	initial_worker_timeout_in_s : int
		? 

	Returns
	-------
	Task 
		A general Task object initialized to the supplied parameters
	"""

	#consider using a task builder classs to make tasks in this method
	return Task(text = text_, image_url = image_url_, budget = budget_, img_alt_txt = img_alt_txt_ , title = title_ , 
					pattern = pattern_ , confidence = confidence_, sample_size = sample_size_, options = options_ , 
					dimensions = dimensions_ , dont_reject = dont_reject_ , pay_all_on_failure = pay_all_on_failure_,
					dry_run = dry_run_, allow_empty_pattern = allow_empty_pattern_, pattern_error_text = pattern_error_text_, 
					wage = wage_, max_value = max_value_, min_value = min_value_, 
					question_timeout_multiplier = question_timeout_multiplier_, 
					initial_worker_timeout_in_s = initial_worker_timeout_in_s_)

def submit_task(channel_,task_):
	"""
	Submits task_ to the gRPC server listening on channel_

	Parameters
    ----------
    channel_ : Channel
    	A gRPC channel
    task_ : Task
    	A Task to be run by Automan

	Returns
	-------
	TaskResponse
		A response from the gRPC server on the outcome of the task. If the response is valid, the outcome
		will be stored in the field 'outcome' of type TaskOutcome. The field return_code determine
		if the response is valid or an error/exception happened. values of the enum are: 
		TaskResponse.VALID 
		TaskResponse.ERROR
		TaskResponse.EXCEPTION

	Notes
	-----
	-fields err_msg and excep_msg set if there is an error or exception, along with err_code and excep_code
	-UNDEFINED_RESP_CODE refers to an unknown response code, if this is seen, if this is seen, check protobuf files and ensure 
	it is the latest version

	"""

	# type check, error check, throw exceptions
	at_task_ = AutomanTask(request = task_)
	client_stub = _make_client_stub(channel_)
	response = client_stub.SubmitTask(at_task_)
	return response

def shutdown_rpc_server(channel_):
	"""
	Shutdown the remote gRPC server

	Parameters
    ----------
    channel_ : Channel
    	A gRPC channel

	"""
	client_stub = _make_client_stub(channel_)
	stat_resp = client_stub.KillServer(Empty())
	return stat_resp


def get_server_status(channel_):
	"""
	Returns the server status

	Returns
	-------
	ServerStatusResponse
		An enum that indicates the server status, with following values:
		ServerStatusResponse.RUNNING 
		ServerStatusResponse.KILLED 
	Notes
	-----
	-UNDEFINED_RESP_CODE refers to an unknown response code, if this is seen, if this is seen, check protobuf files and ensure 
	it is the latest version
	"""
	client_stub = _make_client_stub(channel_)
	stat_resp = client_stub.ServerStatus(Empty())
	return stat_resp

def register_adapter_to_server(channel_, adptr_):
	"""
	Registers the adapter to the gRPC server to carry out Automan jobs

	Parameters
    ----------
    channel_ : Channel
    	A gRPC channel
	adptr_ : AdapterCredentials
		an adapter object for authenticating to the crowdsource back-end

	Returns
	-------
	RegistrationResponse
		An enum that indicates whether the adapter was registered successfully or not, with following values:
		RegistrationResponse.OKAY 
		RegistrationResponse.FAILED 
	Notes
	-----
	-UNDEFINED_RESP_CODE refers to an unknown response code, if this is seen, check protobuf files and ensure 
	it is the latest version
	"""
	client_stub = _make_client_stub(channel_)
	response = client_stub.RegisterAdapter(adptr_)
	return response
