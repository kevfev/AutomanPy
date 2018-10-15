from grpc_gen_classes.automanlib_rpc_pb2 import *
from grpc_gen_classes.automanlib_classes_pb2 import *
from grpc_gen_classes.automanlib_wrappers_pb2 import *
from grpc_gen_classes import automanlib_rpc_pb2_grpc as rpclib
from pyautomanexceptions import *
import grpc
from os import path, devnull
from time import sleep
from subprocess import Popen


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
    	returns True if the adapter validates (not authenticates) successfully, or
    	Raises an exception if the adapter is not created properly

    Raises
	------
	AdapterError: Indicates there was an error creating the adapter. Method will set error msg
					to indicate which required field was not found
	"""

	required_strings = ["access_id", "access_key", "type"]
	for req in required_strings:
		if req not in adapter:
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

	return rpclib.PyautomanPrototypeStub(channel_)

def make_adapter(adapter, lglvl, lg):
	"""
	Makes an adapter from the provided parameter credentials

	Parameters
	----------
	adapter : dict
		Dictionary that holds the backend login credentials, and any additional options
	lglvl : str
		The log level for the Automan Worker on the RPC server

	Returns
	-------
	AdapterCredentials
		an adapter object for authenticating to the crowdsource back-end, or raises an exception if there was a problem
		encountered

	Raises
	------
	AdapterError: 	Indicates there was an error creating the adapter, see msg field of exception for more info
	"""
	if isGoodAadapter(adapter):
		acc_id = adapter.pop("access_id")
		acc_key =  adapter.pop("access_key")
		ad_type_str = adapter.pop("type")
		if ad_type_str.lower() == "mturk":
			return AdapterCredentials(adptr_type = AdapterCredentials.MTURK, 
										access_id = acc_id, 
										access_key = acc_key, 
										adapter_options = adapter, 
										logging = lg,
										log_level = lglvl)
		else:
			raise AdapterError("unsupported adapter type. Currently, the only supported crowdsource backend is mturk")
	else:
		raise AdapterError("missing required field in dict in adapter dict. The required fields are : access_id, access_key, type")

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
	print "Warning: Making an insecure gRPC channel"
	return grpc.insecure_channel(address_+":"+port_)

def make_est_task(text_, budget_, image_url_=None, img_alt_txt_ = None, title_ = None, confidence_ = None, confidence_int_ = None,
				sample_size_ = -1, dont_reject_ = False, pay_all_on_failure_ = True, dry_run_ = False, 
				wage_ = None, max_value_ = None, min_value_ = None, question_timeout_multiplier_ = None, 
				initial_worker_timeout_in_s_ = None):
	"""
	Makes an estimation task for an Automan object to service

	Parameters
	----------
	see make_task for description

	Returns
	-------
	Task 
		A Task object initialized to the supplied parameters
	------
	"""
	task = make_task(text_=text_, image_url_=image_url_, budget_=budget_, img_alt_txt_=img_alt_txt_ , title_=title_ , 
						confidence_=confidence_ ,confidence_int_ = confidence_int_,sample_size_=sample_size_ , dont_reject_ =dont_reject_ , 
						pay_all_on_failure_ =pay_all_on_failure_  , dry_run_ = dry_run_ , wage_ = wage_, 
						max_value_ = max_value_ , min_value_ = min_value_ , 
						question_timeout_multiplier_ = question_timeout_multiplier_ , 
						initial_worker_timeout_in_s_ =initial_worker_timeout_in_s_) 

	timeout = int(initial_worker_timeout_in_s_) * int(initial_worker_timeout_in_s_)
	automan_task = AutomanTask(estimate=EstimateTask(task=task), timeout = timeout)
	return automan_task

def make_rad_task(text_, options_, budget_, image_url_=None, img_alt_txt_ = None, title_ = None, confidence_ = None, 
				dont_reject_ = False, pay_all_on_failure_ = True, dry_run_ = False, 
				wage_ = None, question_timeout_multiplier_ = None, initial_worker_timeout_in_s_ = None):
	"""
	Makes a radio task for an Automan object to service

	Parameters
	----------
	see make_task for description

	Returns
	-------
	Task 
		A Task object initialized to the supplied parameters
	------
	"""
	opts = make_options(options_)
	task = make_task(text_=text_, image_url_=image_url_, budget_=budget_, img_alt_txt_=img_alt_txt_ , title_=title_ , 
						confidence_=confidence_ ,dont_reject_ =dont_reject_ , options_=opts,
						pay_all_on_failure_ =pay_all_on_failure_  , dry_run_ = dry_run_ , wage_ = wage_, 
						question_timeout_multiplier_ = question_timeout_multiplier_ , 
						initial_worker_timeout_in_s_ =initial_worker_timeout_in_s_) 
	timeout = int(initial_worker_timeout_in_s_) * int(initial_worker_timeout_in_s_)
	automan_task = AutomanTask(radio=RadioTask(task=task), timeout = timeout)
	return automan_task

def make_task(text_, budget_, image_url_=None, img_alt_txt_ = None, title_ = None, pattern_ = None, confidence_ = None, 
			confidence_int_ = None,sample_size_ = -1, options_ = None, dimensions_ = None, dont_reject_ = False, pay_all_on_failure_ = True,
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
	budget_ : float
		The total budget allocated for this task
	img_alt_txt_ : str
		The alternate text description for the image, for browser use
	pattern_ : str 
		The expected pattern (Freetext tasks only)
	confidence_ : float 
		The desired confidence level of the estimation	
	confidence_int_ : float
			The desired confidence interval. If 'None', an Unconstrained Confidence Internal is used,
			if set to a value, a symmetric confidence interval of with confidence_int is used.	
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
	wage_ : float
		? 
	max_value_: float
		? 
	min_value_ : float
		? 
	question_timeout_multiplier_ : float
		Value of this multiplier determines how long the question lives on the crowdsource backend before expiring.
		For example: if this value is 60, and the initial_worker_timeout_in_s_ is 60, the question will live for 1 hour
	initial_worker_timeout_in_s_ : int
		The time limit for the worker to complete the task once accepted  

	Returns
	-------
	Task 
		A general Task object initialized to the supplied parameters
	"""
	t = Task(text = text_, image_url = image_url_, budget = budget_, img_alt_txt = img_alt_txt_ , title = title_ , 
					pattern = pattern_ , confidence = confidence_, confidence_int = confidence_int_, sample_size = sample_size_, options = options_ , 
					dimensions = dimensions_ , dont_reject = dont_reject_ , pay_all_on_failure = pay_all_on_failure_,dry_run = dry_run_, 
					allow_empty_pattern = allow_empty_pattern_, pattern_error_text = pattern_error_text_, wage = wage_, max_value = max_value_, 
					min_value = min_value_, question_timeout_multiplier = question_timeout_multiplier_, initial_worker_timeout_in_s = initial_worker_timeout_in_s_)

	return t

def make_options(options_):
	"""
	Creates the OptionsTuple object for tasks that require answer option choices to be specified

	Parameters
	----------
	options : dict(String -> (String) or String -> (String, String))
			A dictionary of possible of possible radio choices: 
				-key of entry represents choice name
				-entries are either:
					- 1-tuples, where the first item is the name(string) of the choice
					- 2-tuples, where the first item is the name(string) of the choice, and the second item is a url(string)
			
	Returns
	-------
	OptionsTuple
		An OptionsTuple object
	"""
	opts = None
	single_tasks=None
	for key in options_.keys():
		if single_tasks is None:
			opts = OptionsTuple()
			if isinstance(options_[key], str):
				single_tasks = True
				opts.tuple_type = OptionsTuple.SINGLE
			elif isinstance(options_[key], tuple):
				single_tasks = False
				opts.tuple_type = OptionsTuple.DOUBLE
			else:
				raise ArgumentError(" badly formed options dict")
		if single_tasks ==True:
			opts.single[key] = options_[key]
		if single_tasks ==False:
			opts.double[key].name = options_[key][0]
			opts.double[key].url = options_[key][1]
	return opts

def submit_task(channel_,automan_task_, adapter_):
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
	gRPC Future TaskResponse
		A future response from the gRPC server on that will hold the outcome of the task. If the future 
		response is valid, the outcome will be stored in the gRPC oneof task_outcome. The calling method will need to
		know what type of outcome to expect . The return_code determines if the response is valid or an error/exception 
		happened. values of the enum are: 
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
	client_stub = _make_client_stub(channel_)
	response = client_stub.SubmitTask.future(automan_task_)
	return response

def start_rpc_server(port=50051, suppress_output = 'all', stdout_file = None, stderr_file = None):
	"""
	Start the remote gRPC server process

	Parameters
    ----------
    port : int
    	The desired port number to have the started server listen on
	suppress_output : string
		Setting for suppressing the output of the RPC server from stdout.
		Values are:
	    		all 	- suppress all output from rpc server
	    		stdout 	- suppress all output from rpc server
	    		file 	- redirect output from rpc server to files specified by 
	    					stdout and stderr 
	    		none 	- suppress no output from rpc server
	"""
	# add check port for correct type and valid range
	cmd_string = [path.dirname(__file__)+"/rpc_server/pack/bin/PyAutoManRpcServer", str(port)]
	stout = open(devnull, 'w')
	sterr = open(devnull, 'w')

	if suppress_output.lower() == "stdout":
		stout = open(devnull, 'w')
		sterr = None
	if suppress_output.lower() == "file":
		print("Redirecting output to file not yet implemented! Defaulting to stdout/stderr")
		#stout = stdout_file
		#sterr = stderr_file
		stout = None
		sterr = None
	if suppress_output.lower() == "none":
		stout = None
		sterr = None

	# launch server and wait for it to get ready
	p = Popen(cmd_string, stdout = stout, stderr = sterr)
	return p

def shutdown_rpc_server(channel_):
	"""
	Shutdown the remote gRPC server process

	Parameters
    ----------
    channel_ : Channel
    	A gRPC channel

	"""
	client_stub = _make_client_stub(channel_)
	stat_resp = client_stub.KillServer(Empty())
	return stat_resp

def register_adapter_to_server(channel_, adptr):
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
	-UNDEFINED_RESP_CODE refers to an unknown response code, if this is seen, check application version
	"""
	client_stub = _make_client_stub(channel_)
	response = client_stub.RegisterAdapter(adptr)
	return response

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

