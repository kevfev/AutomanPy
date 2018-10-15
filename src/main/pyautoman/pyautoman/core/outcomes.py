from grpc_gen_classes.automanlib_rpc_pb2 import TaskResponse
from pyautomanexceptions import ArgumentError, UnsupportedServerError, AdapterError, RPCServerError
from grpc import FutureTimeoutError, FutureCancelledError
class Outcome():
	"""
	The Outcome Class. This class holds the result of an Automan computation

	Attributes
	----------
	_future_task_resp : TaskResponse
		A private variable, stores the future representing the response from the server for the estimation task. 
		The future will be resolved by calling isConfident, isLowConfidence, or isOverBudget.
	_evaluated : boolean
		A private variable indicating whether the object's stored future has been resolved (True) or not (False)
	_outcome_type_val : str
		A private variable that holds the type of outcome, can be "CONFIDENT", "LOW_CONFIDENCE", and "OVERBUDGET"
	cost : float
		The cost of the task. Only set if the outcome is "CONFIDENT" or "LOW_CONFIDENCE"
	conf : float
		The confidence of the estimate. Only set if the outcome is "CONFIDENT" or "LOW_CONFIDENCE"
	need : float
		The amount needed to retry posting the task. Only set if the outcome is "OVERBUDGET"
	have : float
		The amount previously budget. Only set if the outcome is "OVERBUDGET"
	"""

	def __init__(self, future_tr):
		"""
		Initialize the fields for an  outcome

		Parameters
		----------
		future_tr : TaskResponse
			A future representing the response from the server for the estimation task. The future will be resolved
			by calling isConfident, isLowConfidence, or isOverBudget.
		"""
		self._future_task_resp = future_tr
		self._evaluated = False
		self._outcome_type_val = None
		self.cost = float('nan')
		self.conf = float('nan')
		self.need = float('nan')
		self.have = float('nan')
		self.types_outcome = {'CONFIDENT':1, 'LOW_CONFIDENCE':2, 'OVERBUDGET':3}

	def _evalOutcome(self,response):
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
			If the response is valid, it returns the outcome of the task. If there was an error or exception, 
			returned by the server the function terminates the script and prints an error message to output

		"""
		raise NotImplementedError("Must implement this method in subclass")

	def _resolveResponse(self, waitTime = None):
		"""
		Resolve the response (the outcome from the future task response) and initializes the correct fields of 
		the EstimateOutcome returned to the user. This method will block.

		Raises
		------
		FutureTimeoutError: 	If a timeout value is passed and the computation does not
								terminate within the allotted time.

		FutureCancelledError: 	If the computation was cancelled.

		Exception: 		If the computation raised an exception, this call will raise
						the same exception.
		"""
		raise NotImplementedError("Must implement this method in subclass")

	def printOutcome(self, timeout = None):
		"""
		Convenient function for printing the output of an outcome

		Raises
		------
		FutureTimeoutError: 	If a timeout value is passed and the computation does not
								terminate within the allotted time.

		FutureCancelledError: 	If the computation was cancelled.

		Exception: 		If the computation raised an exception, this call will raise
						the same exception.
		"""
		raise NotImplementedError("Must implement this method in subclass")

	def outcomeType(self):
		"""
		Returns the string outcome type
		Returns
		-------
		String
			The outcome type. One of: CONFIDENT, LOW_CONFIDENCE or OVERBUDGET

		"""
		return self._outcome_type_val

	def done(self, timeout = None):
		"""
		waits for the future to resolve,blocks

		"""
		self._resolveResponse(waitTime = timeout)

	def isDone(self):
		"""
		Returns a boolean indicating whether the outcome's future is resolved or not as yet
		Returns
		-------
		boolean
			True if the outcome's future is resolved, False otherwise. Does not block.

		"""
		return self._evaluated

	def isConfident(self, timeout = None):
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
			self._resolveResponse(waitTime = timeout)
		return 'ESTIMATE' == self._outcome_type_val

	def isLowConfidence(self, timeout = None):
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
			self._resolveResponse(waitTime = timeout)
		return 'LOW_CONFIDENCE' == self._outcome_type_val

	def isOverBudget(self, timeout = None):
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
			self._resolveResponse(waitTime = timeout)
		return 'OVERBUDGET' == self._outcome_type_val

class RadioOutcome(Outcome):
	"""
	The RadioOutcome Class. This class holds the result of an Automan radio computation

	Attributes
	----------
	In addition to the attributes of the base super class, Outcome, EstimateOutcomes have:

	low : float
		The lowest valued worker response. Only set if the outcome is "CONFIDENT" or "LOW_CONFIDENCE"
	est : float
		The estimated value. Only set if the outcome is "CONFIDENT" or "LOW_CONFIDENCE"
	high : float
		The highest valued worker response. Only set if the outcome is "CONFIDENT" or "LOW_CONFIDENCE"
	"""
	def __init__(self, future_tr):
		"""
		Initialize the fields for an estimation outcome, and general outcome fields of superclass

		Parameters
		----------
		future_tr : TaskResponse
			A future representing the response from the server for the estimation task. The future will be resolved
			by calling isConfident, isLowConfidence, or isOverBudget.
		"""
		Outcome.__init__(self,future_tr)
		self.answer = None

	def _evalOutcome(self,response):
		ret_string = None
		if response.return_code == TaskResponse.VALID:
			return response.outcome.radio_outcome
		if response.return_code == TaskResponse.UNDEFINED_RESP_CODE:
			ret_string= "ERROR: An undefind response code was returned. Application may be out of data or there is an error on the grpc server side"
		if response.return_code == TaskResponse.ERROR:
			ret_string = "ERROR: An error occured \n"+ "Message: "+response.err_msg
		if response.return_code == TaskResponse.EXCEPTION:
			ret_string ="EXCEPTION: An exception occured \n"+ "Message: "+response.excep_msg

		raise RPCServerError(ret_string)

	def _resolveResponse(self, waitTime = None):
		try:
			future = self._future_task_resp.result(timeout = waitTime)
		except FutureTimeoutError:
			print("TimeoutError: This outcome timed out before its future resolved.")
			raise
		except FutureCancelledError:
			print("CancelledError: This gRPC call has been cancelled")
			raise
		except Exception: 
			raise

		outcome = self._evalOutcome(future)
		if self.types_outcome['OVERBUDGET'] ==  outcome.outcome_type:
			self.need= outcome.need
			self.have = outcome.have
			self._outcome_type_val = "OVERBUDGET"
		else:
			self.answer = outcome.answer.option
			self.conf = outcome.answer.conf
			self.cost = outcome.answer.cost
			if self.types_outcome['CONFIDENT'] ==  outcome.outcome_type:
				self._outcome_type_val = "CONFIDENT"
			if self.types_outcome['LOW_CONFIDENCE'] ==  outcome.outcome_type:
				self._outcome_type_val = "LOW_CONFIDENCE"
		self._evaluated = True

	def printOutcome(self, timeout = None):
		if(self.isConfident(timeout)):
			print("Outcome: Confident Answer")
			print("Answer %s "%(self.answer))


		if(self.isLowConfidence(timeout)):
			print("Outcome: Low Confidence Answer")
			print("Answer %s "%(self.answer))

		if(self.isOverBudget(timeout)):
			print("Outcome: Over Budget")
			print(" need: %f have:%f"%(self.need, self.have))

class EstimateOutcome(Outcome):
	"""
	The EstimateOutcome Class. This class holds the result of an Automan estimation computation

	Attributes
	----------
	In addition to the attributes of the base super class, Outcome, EstimateOutcomes have:

	low : float
		The lowest valued worker response. Only set if the outcome is "CONFIDENT" or "LOW_CONFIDENCE"
	est : float
		The estimated value. Only set if the outcome is "CONFIDENT" or "LOW_CONFIDENCE"
	high : float
		The highest valued worker response. Only set if the outcome is "CONFIDENT" or "LOW_CONFIDENCE"
	"""
	def __init__(self, future_tr):
		"""
		Initialize the fields for an estimation outcome, and general outcome fields of superclass

		Parameters
		----------
		future_tr : TaskResponse
			A future representing the response from the server for the estimation task. The future will be resolved
			by calling isConfident, isLowConfidence, or isOverBudget.
		"""
		Outcome.__init__(self,future_tr)
		self.low = float('nan')
		self.high = float('nan')
		self.est = float('nan')

	def _evalOutcome(self,response):
		ret_string = None
		if response.return_code == TaskResponse.VALID:
			return response.outcome.estimate_outcome
		if response.return_code == TaskResponse.UNDEFINED_RESP_CODE:
			ret_string= "ERROR: An undefind response code was returned. Application may be out of data or there is an error on the grpc server side"
		if response.return_code == TaskResponse.ERROR:
			ret_string = "ERROR: An error occured \n"+ "Message: "+response.err_msg
		if response.return_code == TaskResponse.EXCEPTION:
			ret_string ="EXCEPTION: An exception occured \n"+ "Message: "+response.excep_msg

		raise RPCServerError(ret_string)

	def _resolveResponse(self, waitTime = None):
		try:
			future = self._future_task_resp.result(timeout = waitTime)
		except FutureTimeoutError:
			print("TimeoutError: This outcome timed out before its future resolved.")
			raise
		except FutureCancelledError:
			print("CancelledError: This gRPC call has been cancelled")
			raise
		except Exception: 
			raise

		outcome = self._evalOutcome(future)
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
			if self.types_outcome['CONFIDENT'] ==  outcome.outcome_type:
				self._outcome_type_val = "CONFIDENT"
			if self.types_outcome['LOW_CONFIDENCE'] ==  outcome.outcome_type:
				self._outcome_type_val = "LOW_CONFIDENCE"
		self._evaluated = True

	def printOutcome(self, timeout = None):
		if(self.isConfident(timeout)):
			print("Outcome: Confident Estimate")
			print("Estimate low: %f high:%f est:%f "%(self.low, self.high, self.est))


		if(self.isLowConfidence(timeout)):
			print("Outcome: Low Confidence Estimate")
			print("Estimate low: %f high:%f est:%f "%(self.low, self.high, self.est))

		if(self.isOverBudget(timeout)):
			print("Outcome: Over Budget")
			print(" need: %f have:%f"%(self.need, self.have))
