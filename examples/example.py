from automanpy.automan import Automan, EstimateOutcome

# make mechanical turk adapter
# sandbox_mode is boolean, if true, will post tasks to MTurk developer sandbox
adapter = {
	"access_id" : "access id here",
	"access_key" : "access key here",
	"sandbox_mode" : "true",
	"type" : "MTurk"
}

# image to submit with our task
photo_url = "https://docs.google.com/uc?id=1kpw8sjiZtJwRlVJ3_tYBo26ZcqAeVb5c"

# make AutoMan object 
# 'suppress_output' sets the how much output from the RPC server to print to stdout. current valid values are
# 		"all" 	- suppress all output
# 		"none "	- show all output 

# 'loglevel' sets the the logging level for Automan. valid values are
#		'debug' - debug level 
#		'info' 	- information level (default)
#		'warn' 	- warnings only
#		'fatal' - fatal messages only
#
# the loglevel is currently set to 'warn', so you will see output from the RPC-Server/Worker-Thread
a = Automan(adapter, server_addr='localhost',port=50051,suppress_output="none", loglevel='warn')

estim = a.estimate(text = "How many cars are in this parking lot?",
	budget = 1.50,
	title = "Car Counting",
	confidence = 0.9,
	question_timeout_multiplier = 5,# uncomment to set question to timeout on mturk,
	initial_worker_timeout_in_s = 30,
	image_url = photo_url)

# NOTE: question_timeout_multiplier (default 500) and initial_worker_timeout_in_s (default = 30)  combine to give 
# tme question will live on on time, given by question_timeout_multiplier * initial_worker_timeout_in_s
# in this example, the question will be available on mturk for 150 seconds, after which it will expire.
# when it expires, automan will attempt to repost the task at double the time and double the reward 
# until budget is exhausted.

if(estim.isConfident()):
	print("Outcome: Estimate")
	print("Estimate low: %f high:%f est:%f "%(estim.low, estim.high, estim.est))


if(estim.isLowConfidence()):
	print("Outcome: Low Confidence Estimate")
	print("Estimate low: %f high:%f est:%f "%(estim.low, estim.high, estim.est))

if(estim.isOverBudget()):
	print("Outcome: Over Budget")
	print(" need: %f have:%f"%(estim.need, estim.have))
