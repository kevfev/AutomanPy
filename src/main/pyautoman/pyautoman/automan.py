import core.automanlib as pyAutomanlib
from core.grpc_gen_classes.automanlib_rpc_pb2 import TaskResponse
from core.grpc_gen_classes.automanlib_classes_pb2 import SymmetricConInt, AsymmetricConInt, UnconstrainedConInt, Task
import sys


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
    error : double
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
    error : double
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
    error : double
    	The desired confidence interval
	"""
	def __init__(self, low_error, high_error):
		self.low_error = low_error
		self.high_error = high_error

	def makeCI():
		return SymmetricConInt(low_err = self.low_error, high_err = self.high_error)

	def addCI(self,task):
		return task.UnconstrainedConInt()

class EstimateOutcome():
	"""
	The Outcome Class. This class holds the result of an Automan computation

    Attributes
    ----------
    outcome : ValueOutcome
        An answer returned from the gRPC server, the estimation result of the automan computation
    outcome_type : int (enum)
    	An int representing the type of the outcome. Possible values are:
    	UNKNOWN = 0;
		ESTIMATE = 1;
		LOW_CONFIDENCE = 2;
		OVER_BUDGET = 3;
	"""

	def __init__(self, future_tr):
		"""
		Ensure necessary fields in adapter are initializated and
		set up the gRPC channel

		Parameters
		----------
		response : TaskResponse
			An future representing the response from the server for the estimation task. The future will be resolved
			by calling isConfident, isLowConfidence, or isOverBudget.
		"""
		self._future_task_resp = future_tr
		self._evaluated = False
		self._outcome_type_val = None
		self.outcome_type = None
		self.low = float('nan')
		self.high = float('nan')
		self.est = float('nan')
		self.cost = float('nan')
		self.conf = float('nan')
		self.need = float('nan')
		self.have = float('nan')


		self.types_outcome = {'ESTIMATE':1, 'LOW_CONFIDENCE':2, 'OVERBUDGET':3}

	def _resolveResponse(self,response):
		"""
		Internal method.  Evaluate the response from the gRPC server. First determine if response is valid.
		The field return_code can take the following values:
			TaskResponse.VALID 
			TaskResponse.ERROR
			TaskResponse.EXCEPTION

        Parameters
        ----------
        response : TaskResponse
            The response from the server

        Returns
        -------
        TaskOutcome
        	If the response is valid, it returns the outcome of the task
        None
            If there was an error or exception, the function terminates the script and prints an error message to output

        """
		ret_string = None
		if response.return_code == TaskResponse.VALID:
			return response.estimate_outcome
		if response.return_code == TaskResponse.UNDEFINED_RESP_CODE:
			ret_string= "ERROR: An undefind response code was returned. Application may be out of data or there is an error on the grpc server side"
		if response.return_code == TaskResponse.ERROR:
			ret_string = "ERROR: An error occured \n"+ "Message: "+response.err_msg
		if response.return_code == TaskResponse.EXCEPTION:
			ret_string ="EXCEPTION: An exception occured \n"+ "Message: "+response.excep_msg

		sys.exit(ret_string)

	def _evalOutcome(self):
		"""
		Evaluates the result of the outcome from the future task response and initializes the correct fields of 
		the EstimateOutcome returned to the user. This method causes isEstimate, isLowConfidence, and isOverBudget
		to block.

		"""
		outcome = self._resolveResponse(self._future_task_resp.result())
		if self.types_outcome['OVERBUDGET'] ==  outcome.outcome_type:
			self.need= outcome.need
			self.have = outcome.have
			self._outcome_type_val = "OVERBUDGET"
		else:
			self.low = outcome.answer.low
			self.high = outcome.answer.high
			self.est = outcome.answer.est
			self.conf = outcome.answer.conf
			self.cost = outcome.answer.cost
			if self.types_outcome['ESTIMATE'] ==  outcome.outcome_type:
				self._outcome_type_val = "ESTIMATE"
			if self.types_outcome['LOW_CONFIDENCE'] ==  outcome.outcome_type:
				self._outcome_type_val = "LOW_CONFIDENCE"
		self._evaluated = True

	def outcomeType(self):
		return self.types_outcome

	def printOutcome(self):
		if(estim.isEstimate()):
			print("Outcome: Estimate")
			print("Estimate low: %f high:%f est:%f "%(estim.low, estim.high, estim.est))


		if(estim.isLowConfidence()):
			print("Outcome: Low Confidence Estimate")
			print("Estimate low: %f high:%f est:%f "%(estim.low, estim.high, estim.est))

		if(estim.isOverBudget()):
			print("Outcome: Over Budget")
			print(" need: %f have:%f"%(estim.need, estim.have))

	def isConfident(self):
		"""
		Evaluates the outcome (if it is not already evaluated) and determines whether the outcome
		type was a confident estimate. This call will block if the future is not yet resolved.

		Returns
		-------
		bool
			True if outcome is an estimate
			False otherwise
		"""
		
		if not self._evaluated:
			self._evalOutcome()
		return 'ESTIMATE' == self._outcome_type_val

	def isLowConfidence(self):
		"""
		Evaluates the outcome (if it is not already evaluated) and determines whether the outcome
		type was a low confidence estimate. This call will block if the future is not yet resolved.

		Returns
		-------
		bool
			True if outcome is a low confidence estimate
			False otherwise
		"""
		if not self._evaluated:
			self._evalOutcome()
		return 'LOW_CONFIDENCE' == self._outcome_type_val

	def isOverBudget(self):
		"""
		Evaluates the outcome (if it is not already evaluated) and determines whether the outcome
		type overbudget. This call will block if the future is not yet resolved.

		Returns
		-------
		bool
			True if outcome is over budget
			False otherwise
		"""
		if not self._evaluated:
			self._evalOutcome()
		return 'OVERBUDGET' == self._outcome_type_val

class Automan():
	"""
	The Automan Class.

    Attributes
    ----------
    adptr : dict
        A dictionary containing the parameters for the adapter
    srvr_addr : str
    	The hostname for the gRPC server
    port : int 
    	The port to connect to on the hostname 
    channel: Channel
    	The gRPC channel to communicate over

    """

	def __init__(self, adapter, server_addr = 'localhost', port = 50051, suppress_output = 'all', stdout =None, stderr = None):
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
	    stdout : string
	    	File path to write RPC server standard output to
	    stderr : string
	    	File path to write RPC server error output to

        """
		self.adptr = pyAutomanlib.make_adapter(adapter["access_id"], adapter["access_key"], sandbox_mode=adapter["sandbox_mode"]) if pyAutomanlib.isGoodAadapter(adapter) else None
		self.srvr_addr = server_addr
		self.port = port
		self.srvr_popen_obj = None
		self.supr_lvl = suppress_output
		self.stdout_file = stdout
		self.stderr_file = stderr
		
		# check adapter to ensure it passed validation
		if self.adptr is None:
			sys.exit("Invalid adapter, ensure that 'access_id', 'access_key' and 'type' are initializated in supplied dictionary")

		# set up channel, start and connect to gRPC server
		self._init_channel(server_addr, port)
		self._start()

	def _start(self):
		print "python client is starting rpc server..."
		self.srvr_popen_obj = pyAutomanlib.start_rpc_server(port=self.port, suppress_output = self.supr_lvl,
			stdout_file = self.stdout_file, stderr_file = self.stderr_file)

	def _shutdown(self):
		"""
		Internal method. Shutdown the gRPC server

		"""
		pyAutomanlib.shutdown_rpc_server(self.channel)

	def _force_shutdown(self):
		"""
		Internal method. Forces shutdown the gRPC server by killing spawned process

		"""
		self.srvr_popen_obj.kill()


	def _init_channel(self, server_addr, port):
		"""
		Internal method. Create the gRPC channel

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
		return 

	def estimate(self, text, budget, image_url, title = "", confidence = 0.95, confidence_int = -1, img_alt_txt = "",sample_size = -1, dont_reject = False, 
				pay_all_on_failure = True, dry_run = False, wage = 11.00, max_value = sys.float_info.max, min_value = sys.float_info.min, question_timeout_multiplier = 500, 
				initial_worker_timeout_in_s = 30):
		"""
		Estimates the answer to the provided task. Calls AutoMan's estimate functionality on the back-end

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
		confidence : double
			The desired confidence level 
		confidence_int : double
			The desired confidence interval. If '-1', an Unconstrained Confidence Internal is used,
			if set to a value, a symmetric confidence interval of with confidence_int is used.
		img_alt_txt : string
			The alternate image text to display on the webpage
		sample_size : int
			The desired sample size 
		dont_reject : boolean
			?
		pay_all_on_failure : boolean
			? 
		dry_run : boolean
			? 
		wage : double
			Minimum wage to pay the worker
		max_value : double
			?
		min_value : double
			?
		question_timeout_multiplier: double
			?
		initial_worker_timeout_in_s : int
			?

        Returns
        -------
        EstimateOutcome
            A wrapper class that contains a future estimation outcome.

        """


		task = pyAutomanlib.make_est_task(text_ = text,
	    								budget_ = budget,
	    								title_ = title,
	    								image_url_ = image_url,
	    								confidence_ = confidence,
	    								confidence_int_ = confidence_int,
	    								img_alt_txt_ = img_alt_txt,
										sample_size_ = sample_size, 
										dont_reject_ = dont_reject, 
										pay_all_on_failure_ = pay_all_on_failure, 
										dry_run_ = dry_run, 
										wage_ = wage, 
										max_value_ = max_value, 
										min_value_ = min_value, 
										question_timeout_multiplier_ = question_timeout_multiplier, 
										initial_worker_timeout_in_s_ = initial_worker_timeout_in_s)
		resp = pyAutomanlib.submit_task(self.channel, task, self.adptr)
		eo = EstimateOutcome(future_tr=resp)
		return eo


