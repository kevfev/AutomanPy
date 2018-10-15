from automanpy.automan import Automan, EstimateOutcome

# make mechanical turk adapter
adapter = {
	"access_id" : "access id here",
	"access_key" : "access key here",
	"sandbox_mode" : "true",
	"type" : "MTurk"
}

# image to submit with our task
photo_url = "https://docs.google.com/uc?id=1ZQ-oL8qFt2tx_T_-thev2O4dsugVbKI2"

# make AutoMan object 
# 'suppress_output' sets the how much output from the RPC server to print to stdout. current valid values are
# 		"all" 	- suppress all output
# 		"none "	- show all output 

# 'loglevel' sets the the logging level for Automan. valid values are
#		'debug' - debug level 
#		'info' 	- information level (default)
#		'warn' 	- warnings only
#		'fatal' - fatal messages only

a = Automan(adapter, server_addr='localhost',port=50051,suppress_output="none", loglevel='fatal')

# spawns 'spawn' number of dummy tasks of same image. Note: each task must have unique text and title for automan to post HIT correctly
task_list = list()
spawn = 20
for i in range(spawn):
	task_list.append(a.estimate(text = "task-%d :How many cars are in this parking lot?"%(i),
	    budget = 1.00,
	    title = "Car Counting-v2-%d"%(i),
	    confidence_int = 10,
#=		question_timeout_multiplier = 40,# uncomment to set question to timeout on mturk, good for testing purposes, set no less than 40. see docs for more detail
		image_url = photo_url)

# this is temporary, in future there will be a better construct for
# handling results from AutoMan as the futures resolve, rather than
# having to manually do this
for task in task_list:
	task.done()

for task in task_list:
	task.printOutcome()