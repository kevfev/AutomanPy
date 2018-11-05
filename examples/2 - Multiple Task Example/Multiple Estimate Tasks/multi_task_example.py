from automanpy.automan import Automan, EstimateOutcome

# make mechanical turk adapter
# sandbox_mode is boolean, if true, will post tasks to MTurk developer sandbox
adapter = {
	"access_id" : "access id here",
	"access_key" : "access key here",
	"sandbox_mode" : "true",
	"type" : "MTurk"
}

# images to submit with our task
images = ["https://docs.google.com/uc?id=1kpw8sjiZtJwRlVJ3_tYBo26ZcqAeVb5c",
			"https://docs.google.com/uc?id=1Gdlsk24_dAP3YP6eT6Q9A_khVPsMpJzL",
			"https://docs.google.com/uc?id=1tN9E4wpacVpFmTaAkgoUeIyBZek5cBv7"]


# logging : string
#			Specifies the log configuration of the AutoMan worker. Values are 
#				'none' 	- no logging 
#				't' 	- log trace only
#				'tm' 	- log trace and use for memoization
#				'tv' 	- log trace and output debug information
#				'tmv' 	- log trace, use for memoization and output debug info
#
# logging is set to none. when doing multiple jobs, memory footprint can be reduced by turning trace/memoization
#	logging off
# 
a = Automan(adapter, server_addr='localhost',port=50051,suppress_output="none", loglevel='warn', logging='none')

# spawns 'spawn' number of dummy tasks of same image. Note: each task must have unique text and title for automan to post HIT correctly
task_list = list()
for i in range(len(images)):
	task_list.append(a.estimate(text = "task-%d :Count the number of vehicles in this parking lot"%(i),
							    budget = 1.50,
							    title = "Car Counting-v2-%d"%(i),
							    confidence = 0.9,
								question_timeout_multiplier = 10,
								image_url = images[i]))

# this is temporary, in future there will be a better construct for
# handling results from AutoMan as the futures resolve, rather than
# having to manually do this
for task in task_list:
	task.done()

for task in task_list:
	task.printOutcome()