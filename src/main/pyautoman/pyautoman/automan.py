import core.automanlib as pyAutomanlib
from core.batchjob import Batch
from core.outcomes import *
from core.grpc_gen_classes.automanlib_rpc_pb2 import TaskResponse, ServerStatusResponse
from core.grpc_gen_classes.automanlib_classes_pb2 import SymmetricConInt, AsymmetricConInt, UnconstrainedConInt, Task
from core.pyautomanexceptions import ArgumentError, UnsupportedServerError, AdapterError, RPCServerError
from time import sleep
import sys
import grpc
import atexit


class ConfidenceInterval():
	"""
	An interface for a confidence interval
	"""
	def makeCI(self,):
		pass

	def addCI(self,task):
		pass

class UnconstrainedCI(ConfidenceInterval):
	"""
	A Symmetric confidence interval
	Attributes
    ----------
    error : float
    	The desired confidence interval
	"""
	def makeCI(self):
		return UnconstrainedConInt()

	def addCI(self,task):
		return task.withUnconstrainedConInt()


class SymmetricCI(ConfidenceInterval):
	"""
	A Symmetric confidence interval
	Attributes
	----------
	error : float
		The desired confidence interval
	"""
	def __init__(self, error):
		self.error = error

	def makeCI(self):
		return SymmetricConInt(err=self.error)

	def addCI(self,task):
		return task.withSymmetricConInt(self)



class AsymmetricCI(ConfidenceInterval):
	"""
	A Symmetric confidence interval
	Attributes
	----------
	error : float
		The desired confidence interval
	"""
	def __init__(self, low_error, high_error):
		self.low_error = low_error
		self.high_error = high_error

	def makeCI():
		return SymmetricConInt(low_err = self.low_error, high_err = self.high_error)

	def addCI(self,task):
		return task.UnconstrainedConInt()

class Automan():
	"""
	The Automan Class.

	Attributes
	----------
	lglvl : int
		An integer representing the desired log verbosity for the AutoMan worker
	srvr_addr : str
		The hostname for the gRPC server
	port : int 
		The port to connect to on the hostname 
	channel: Channel
		The gRPC channel to communicate over
	srvr_popen_obj : Popen 
		The Popen object returned when the RPC AutoMan scala server is started
	supr_lvl : string 
		Specifies how much of the output to suppress from the RPC server
	"""

	#dicts declared here are used internally for convenience to map user supplied strings to integers
	LogLevels = {
		'debug' : 0,
		'info' : 1,
		'warn' : 2,
		'fatal' : 3
	}

	Logging = {
		'tm' : 0,
		'none' : 1,
		't' : 2,
		'tv' : 3,
		'tvm' : 4
	}
	SupprOutVals = ['all', 'stdout', 'none']
	LogLevelVals = ['debug','info','warn','fatal']
	LoggingVals =  ['none','t','tm','tv','tmv']

	#max number of attempts to connect to RPC server when attempting to spawn a new one
	MAX_CON_TRIES = 20

	def __init__(self, adapter, server_addr = 'localhost', port = 50051, suppress_output = 'all', 
					loglevel = 'fatal', logging='none', stdout =None, stderr = None, testmode=False):
		"""
		Ensure necessary fields in adapter are initializated and
		set up the gRPC channel

		Parameters
		----------
		adapter : dict
			A dictionary containing the parameters for the adapter
		server_addr : str
			The hostname for the gRPC server
		port : int 
			The port to connect to on the hostname 
		suppress_output : string
			Specifies how much of the output to suppress from the RPC server. Values are:
				all 	- suppress all output from rpc server
				stdout 	- suppress all output from rpc server
				file 	- redirect output from rpc server to files specified by 
							stdout and stderr 
				none 	- suppress no output from rpc server
		loglevel : string
			Specifies the AutoMan worker log level, for setting the level of output from AutoMan. values
				'debug' - debug level 
				'info' 	- information level (default)
				'warn' 	- warnings only
				'fatal' - fatal messages only
		logging : string
			Specifies the log configuration of the AutoMan worker. Values are 
				'none' 	- no logging 
				't' 	- log trace only
				'tm' 	- log trace and use for memoization
				'tv' 	- log trace and output debug information
				'tmv' 	- log trace, use for memoization and output debug info
		testmode : bool
			Specifies whether the object is being created in test mode. Test mode does not start the RPC Server
		[NOT YET IMPLEMENTED]
		stdout : string
			File path to write RPC server standard output to
		stderr : string
			File path to write RPC server error output to
		
		Raises
		------
		AdapterError: Indicates there was an error creating the adapter, see msg field of exception for more info
		ArgumentError: Indicates there was an error with one of the supplied arguments
		UnsupportedServerError: Currently, only local servers (server_addr ='localhost') is supported, this is thrown 
								the user intends to create a server that is not on localhost

		"""

		# type checking, basic error checking
		if not isinstance(adapter, dict): 
			raise ArgumentError("adapter must be of type dict")
		if not isinstance(server_addr, str) or not server_addr.strip(): 
			raise ArgumentError("server_addr must be of type str (only 'localhost' supported), cannot be empty")
		if not isinstance(port, int) or port<=0: 
			raise ArgumentError("port must be of type int, must be greater than 0")
		if not isinstance(suppress_output, str) or not suppress_output.strip() or suppress_output.strip() not in Automan.SupprOutVals: 
			raise ArgumentError("suppress_output must be of type str, cannot be empty")
		if not isinstance(loglevel, str) or not loglevel.strip() or loglevel.strip() not in Automan.LogLevelVals: 
			raise ArgumentError("loglevel must be of type str, cannot be empty")
		if not isinstance(logging, str) or not logging.strip() or logging.strip() not in Automan.LoggingVals: 
			raise ArgumentError("logging must be of type str, cannot be empty")

		# these checks will become relevant when file logging is in place
		#if stdout and not isinstance(stdout, str): raise ArgumentError("stdout must be of type str (desired path to file)")
		#if stderr and not isinstance(stderr, str): raise ArgumentError("stderr must be of type str (desired path to file)")

		# this is only temporary
		if server_addr.lower() != "localhost":
			raise UnsupportedServerError()

		self.lglvl = Automan.LogLevels.get(loglevel.lower(), Automan.LogLevels['fatal'])
		self.lg =  Automan.Logging.get(logging.lower(), Automan.Logging['tm'])
		self.srvr_addr = server_addr
		self.port = port
		self.srvr_popen_obj = None
		self.supr_lvl = suppress_output
		self.stdout_file = stdout
		self.stderr_file = stderr
		self.channel = None

		try:
			_adptr = pyAutomanlib.make_adapter(adapter, self.lglvl, self.lg) 
		except AdapterError:
			raise
		self.adptr = _adptr

		# set up channel, start and connect to gRPC server
		chanl = self._init_channel(server_addr, port)

		if not testmode:
			self._start()
			self._register_adptr()
			@atexit.register
			def _shutdown():
				"""
				Private method. Shutdown the gRPC server

				"""
				pyAutomanlib.shutdown_rpc_server(chanl)

	def _start(self, sleep_time = 5):
		"""
		Private method, used to start the gRPC AutoMan server on the specified channel.  If a server is already started on
		this channel, the client will send requests. If a server is not started, the client will start one and wait until it is ready.

		"""
		try:
			resp = pyAutomanlib.get_server_status(self.channel)
		except grpc.RpcError as rpc_err:
			if rpc_err.code() == grpc.StatusCode.UNAVAILABLE:
				self.srvr_popen_obj = pyAutomanlib.start_rpc_server(port=self.port, 
																	suppress_output = self.supr_lvl,
																	stdout_file = self.stdout_file, 
																	stderr_file = self.stderr_file)

				try_count = 0
				while(try_count < Automan.MAX_CON_TRIES):
					try:
						resp = pyAutomanlib.get_server_status(self.channel)
						return
					except grpc.RpcError as rpc_err:
						sleep(sleep_time)
					try_count = try_count + 1

				self.srvr_popen_obj.kill()
				raise RPCServerError("Attempted to start RPC server process, but unable to communicate with it after 20 tries. Client quitting ")
			else:
				raise RPCServerError("Unable to start server:\n"+rpc_err.details())
	
	def _register_adptr(self):
		"""
		Private method, used to register an adapter with the server

		"""
		# handle response
		resp = pyAutomanlib.register_adapter_to_server(self.channel, self.adptr)

	def _force_svr_shutdown(self):
		"""
		Private method. Forces shutdown the gRPC server by killing spawned process

		"""
		self.srvr_popen_obj.kill()

	def shutdown(self):
		"""
		Shutdown the gRPC server

		"""
		# handle response
		resp = pyAutomanlib.shutdown_rpc_server(self.channel)


	def _init_channel(self, server_addr, port):
		"""
		Private method. Create the gRPC channel

		Parameters
		----------
		server_addr : str
			The hostname for the gRPC server
		port : int 
			The port to connect to on the hostname 

		Returns
		-------
		Channel
			A channel that connects to the gRPC back-end server

		"""
		self.channel = pyAutomanlib.make_channel(server_addr,str(port))
		return self.channel

	def _args_check(self,  budget=None, image_url=None, confidence=None, confidence_int=None, dry_run=None, dont_reject=None,
					initial_worker_timeout_in_s=None, img_alt_txt=None, max_value=None, min_value=None, options = None,
					pay_all_on_failure=None, question_timeout_multiplier=None,  sample_size=None, text=None,title=None,  wage=None,
					options_required=False):
		'''
		Parameters
		----------
		The various parameters that each task can have, see task types for details on parameters

		Returns
		-------
		Nothing

		Raises
		------
		ArgumentError: Indicates there was an error with one of the supplied arguments

		'''
		max_conf_int=100
		min_conf_int=50
		max_conf_flo=1.0
		min_conf_flo=0.5
		#special check for certain tasks that require options to be specified
		if options_required:
			if options is None or not isinstance(options, dict):
				raise ArgumentError("(required argument) options must be a dictionary, where dict key is type string and entries are tuples of type (string[name]), (string[name],string[url])")
			if options is not None:
				singles_test = [isinstance(options[key], str) for key in options.keys()]
				doubles_test = [isinstance(options[key], tuple) and isinstance(options[key][0], str) and isinstance(options[key][1], str) for key in options.keys()]
			if not((all(singles_test) and not any(doubles_test)) or (all(doubles_test) and not any(singles_test))):
				raise ArgumentError("entries of options dict must be tuples of type (string[name]), (string[name],string[url]). Note: cannot mix the two formats")
		
		# type checking and basic error checking
		# -1 specifies use default value for parameter, do not need ot check
		if budget is None or (not isinstance(budget, (int, float)) or budget <= 0): raise ArgumentError("(required argument) budget must be of type float, must be strictly greater than 0")
		if confidence is not None and (not isinstance(confidence, (int, float)) or ((confidence<min_conf_int or confidence>max_conf_int) and (confidence<min_conf_flo or confidence>max_conf_flo))): raise ArgumentError("confidence must be of type float, must be strictly greater than 0")
		if confidence_int is not None and confidence_int != -1:
			if not isinstance(confidence_int, (int, float)) or confidence_int <= 0: raise ArgumentError("confidence_int must be of type float, must be strictly greater than 0")
		if dry_run is not None and not isinstance(dry_run, bool): raise ArgumentError("dry_run must be of type bool")
		if dont_reject is not None and not isinstance(dont_reject, bool): raise ArgumentError("dont_reject must be of type bool")
		if initial_worker_timeout_in_s is not None and (not isinstance(initial_worker_timeout_in_s, int) or initial_worker_timeout_in_s <= 0): raise ArgumentError("initial_worker_timeout_in_s must be of type int, must be strictly greater than 0")
		if image_url is not None and not isinstance(image_url, str): raise ArgumentError("image_url must be of type str")
		if img_alt_txt is not None and not isinstance(img_alt_txt, str): raise ArgumentError("img_alt_txt must be of type str")
		if max_value is not None and (not isinstance(max_value, (int, float))): raise ArgumentError("max_value must be of type float, must be strictly greater than 0")
		if min_value is not None and (not isinstance(min_value, (int, float))): raise ArgumentError("min_value must be of type float, must be strictly greater than 0")
		if pay_all_on_failure is not None and not isinstance(pay_all_on_failure, bool): raise ArgumentError("pay_all_on_failure must be of type bool")
		if question_timeout_multiplier is not None and (not isinstance(question_timeout_multiplier, int) or question_timeout_multiplier <= 0): raise ArgumentError("question_timeout_multiplier must be of type int, must be strictly greater than 0")
		if sample_size is not None and sample_size != -1:
			if not isinstance(sample_size, int) or sample_size <= 0: raise ArgumentError("sample_size must be of type int, must be strictly greater than 0")
		if text is None or (not isinstance(text, str) or not text.strip()): raise ArgumentError("(required argument) text must be of type str, cannot be empty")
		if title is not None and not isinstance(title, str): raise ArgumentError("title must be of type str")
		if wage is not None and (not isinstance(wage, (int, float)) or wage <= 0): raise ArgumentError("wage must be of type float, must be strictly greater than 0")
		
	
	def estimateBatchUrl(self, text=None, budget=None, image_urls=None, title = "", confidence = 0.95, confidence_int = -1, img_alt_txt = "",sample_size = -1, dont_reject = True, 
				pay_all_on_failure = True, dry_run = False, wage = 11.00, max_value = sys.float_info.max, min_value = sys.float_info.min, question_timeout_multiplier = 500, 
				initial_worker_timeout_in_s = 30):
		if len(image_urls) < 2: raise ArgumentError("batch estimation method requires list of urls as input, at least size 2")
		# check arg types
		self.args_check(text, budget, image_url, title, confidence, confidence_int, img_alt_txt,sample_size, dont_reject, 
						pay_all_on_failure, dry_run, wage, max_value, min_value, question_timeout_multiplier, 
						initial_worker_timeout_in_s)

		job_list = list()
		for url in image_urls:
			job_list.append(estimate(text=text, budget=budget, image_url=image_url, title=title, confidence = confidence, confidence_int = confidence_int, 
				img_alt_txt = img_alt_txt ,sample_size = sample_size, dont_reject = dont_reject, pay_all_on_failure = pay_all_on_failure, 
				dry_run = dry_run, wage = wage, max_value = max_value, min_value = min_value, question_timeout_multiplier = question_timeout_multiplier, 
				initial_worker_timeout_in_s = initial_worker_timeout_in_s))
		batch = Batch(job_list)

		return batch

	def estimate(self, text=None, budget=None, confidence = 0.95, confidence_int = -1, dont_reject = True, dry_run = False,initial_worker_timeout_in_s = 30, 
				img_alt_txt = "",image_url="", max_value = sys.float_info.max, min_value = sys.float_info.min, 
				pay_all_on_failure = True, question_timeout_multiplier = 500, sample_size = -1,  title = "",wage = 11.00):
		"""
		Estimates the answer to the provided task. Calls AutoMan's estimate functionality on the back-end

		Parameters
		----------
		text : str
			The text description of the task, to display to workers on the crowdsource platform
		budget : float
			The total budget allocated for this task
		confidence : float
			The desired confidence level 
		confidence_int : float
			The desired confidence interval. If '-1', an Unconstrained Confidence Internal is used,
			if set to a value, a symmetric confidence interval of with confidence_int is used.
		dont_reject : boolean
			?
		dry_run : boolean
			? 
		initial_worker_timeout_in_s : int
			The time limit for the worker to complete the task once accepted  
		img_alt_txt : str
			The alternate image text to display on the webpage
		image_url : str
			The url of the image for the task
		max_value : float
			The maximum value in the range of expected answers 
		min_value : float
			The minimum value in the range of expected answers 
		pay_all_on_failure : boolean
			? 
		question_timeout_multiplier : float
			Value of this multiplier determines how long the question lives on the crowdsource backend before expiring.
			For example: if this value is 60, and the initial_worker_timeout_in_s_ is 60, the question will live for 1 hour
		sample_size : int
			The desired sample size 
		title : str
			The title for the task, to display to workers on the crowdsource platform
		wage : float
			Minimum hourly wage, used to calculate worker reward based on given initial_worker_timeout_in_s

		Returns
		-------
		EstimateOutcome
			A wrapper class that contains a future estimation outcome.

		Raises
		------
		ArgumentError: Indicates there was an error with one of the supplied arguments
		"""
		# check arg types, raise errors
		self._args_check(text=text, budget=budget, image_url=image_url, title=title, confidence=confidence, confidence_int=confidence_int, 
						img_alt_txt=img_alt_txt, sample_size=sample_size, dont_reject=dont_reject, pay_all_on_failure=pay_all_on_failure, 
						dry_run=dry_run, wage=wage, max_value=max_value, min_value=min_value, 
						question_timeout_multiplier=question_timeout_multiplier, initial_worker_timeout_in_s=initial_worker_timeout_in_s)

		task = pyAutomanlib.make_est_task(text_ = text,
										budget_ = float(budget),
										title_ = title,
										image_url_ = image_url,
										confidence_ = float(confidence),
										confidence_int_ = float(confidence_int),
										img_alt_txt_ = img_alt_txt,
										sample_size_ = sample_size, 
										dont_reject_ = dont_reject, 
										pay_all_on_failure_ = pay_all_on_failure, 
										dry_run_ = dry_run, 
										wage_ = float(wage),
										max_value_ = float(max_value),
										min_value_ = float(min_value),
										question_timeout_multiplier_ = question_timeout_multiplier,
										initial_worker_timeout_in_s_ = initial_worker_timeout_in_s)
		try:
			resp = pyAutomanlib.submit_task(self.channel, task, self.adptr)
			eo = EstimateOutcome(future_tr=resp)
			return eo
		except:
			self._force_svr_shutdown()
			raise

	def radio(self, text=None, budget=None, options=None, confidence = 0.95, dont_reject = True, dry_run = False,initial_worker_timeout_in_s = 30, 
				img_alt_txt = "",image_url="", pay_all_on_failure = True, question_timeout_multiplier = 500, title = "",wage = 11.00):
		"""
		Estimates the answer to the provided task. Calls AutoMan's estimate functionality on the back-end

		Parameters
		----------
		text : str
			The text description of the task, to display to workers on the crowdsource platform
		budget : float
			The total budget allocated for this task
		options : dict(String -> (String) or String -> (String, String))
			A dictionary of possible of possible radio choices: 
				-key of entry represents choice name
				-entries are either:
					- 1-tuples, where the first item is the name(string) of the choice
					- 2-tuples, where the first item is the name(string) of the choice, and the second item is a url(string)
		confidence : float
			The desired confidence level 
		dont_reject : boolean
			?
		dry_run : boolean
			? 
		initial_worker_timeout_in_s : int
			The time limit for the worker to complete the task once accepted  
		img_alt_txt : str
			The alternate image text to display on the webpage
		image_url : str
			The url of the image for the task
		pay_all_on_failure : boolean
			? 
		question_timeout_multiplier : float
			Value of this multiplier determines how long the question lives on the crowdsource backend before expiring.
			For example: if this value is 60, and the initial_worker_timeout_in_s_ is 60, the question will live for 1 hour
		title : str
			The title for the task, to display to workers on the crowdsource platform
		wage : float
			Minimum hourly wage, used to calculate worker reward based on given initial_worker_timeout_in_s

		Returns
		-------
		EstimateOutcome
			A wrapper class that contains a future estimation outcome.

		Raises
		------
		ArgumentError: Indicates there was an error with one of the supplied arguments
		"""
		# check arg types, raise errors
		self._args_check(text=text, budget=budget, image_url=image_url, title=title, confidence=confidence, 
						img_alt_txt=img_alt_txt, dont_reject=dont_reject, pay_all_on_failure=pay_all_on_failure, 
						dry_run=dry_run, wage=wage, question_timeout_multiplier=question_timeout_multiplier, 
						options=options, initial_worker_timeout_in_s=initial_worker_timeout_in_s, options_required=True)

		task = pyAutomanlib.make_rad_task(text_ = text,
										budget_ = float(budget),
										options_ =options,
										title_ = title,
										image_url_ = image_url,
										confidence_ = float(confidence),
										img_alt_txt_ = img_alt_txt,
										dont_reject_ = dont_reject, 
										pay_all_on_failure_ = pay_all_on_failure, 
										dry_run_ = dry_run, 
										wage_ = float(wage),
										question_timeout_multiplier_ = question_timeout_multiplier,
										initial_worker_timeout_in_s_ = initial_worker_timeout_in_s)
		try:
			resp = pyAutomanlib.submit_task(self.channel, task, self.adptr)
			ro = RadioOutcome(future_tr=resp)
			return ro
		except:
			self._force_svr_shutdown()
			raise