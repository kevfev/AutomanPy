from outcomes import *
from pyautomanexceptions import ArgumentError, UnsupportedServerError, AdapterError



class Batch():
	"""
	The Batch class. A collection of (possibly unresolved future) EstimateOutcomes, representing
	the result of a batch task submission.

	Attributes
	----------
	outcomes : list
		A list of outcomes, in the order in which the tasks submitted (order of image_urls)
	"""

	def __init__(self, outcomes):
		"""
		Parameters
		----------
		outcomes : list
			A list of futures, representing the future outcome of each task submitted to the server
		"""
		if not isinstance(outcomes, list): 
			raise ArgumentError("Cannot create Batch object: outcomes must be a list")
		for outcome in outcomes:
			if not isinstance(outcome, EstimateOutcome): 
				raise ArgumentError("Cannot create Batch object: each item in the list of outcomes must be of type EstimateOutcome")

		self.outcomes = outcomes

	def wait_all_done(self):
		"""
		Method blocks until the future of every outcome in the batch is resolved

		"""
		for outcome in self.outcomes:
			outcome.done()

	def as_done(self):
		"""
		Method yields the next resolved outcome

		"""
		outcomes_ = self.outcomes.copy()
		while outcomes_:
			for i, outcome in enumerate(outcomes_):
				if outcome.isDone():
					yield outcomes_.pop(i)
			print "sleeptime happens"
			sleep(2)
		return

	def apply(self, callable_fn):
		"""
		Method takes a function that is applied to each outcome as it's future is resolved, and yields the result

		"""
		outcomes_ = self.as_done()
		for outcome in outcomes_:
			yield callable_fn(outcome)
				
	def get(self, i):
		"""
		Method returns the EstimateOutcome at index i

		"""
		# ensure future of outcome is resolved before returning it
		outcomes[i].done()
		return self.outcomes[i]

