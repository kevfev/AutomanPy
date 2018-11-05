from automanpy.automan import Automan, RadioOutcome

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
instructions_text = "Choose the matching image "
titl = "Image match"

#options dictionary, where the choice tuple is a 2-tuple (string,string), which is (choice, url)
opts = dict(choice1=('a',night1),choice2=('b',night2), choice3=('c',night3),choice4=('d',demo_url))

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

estim = a.radio(text = instructions_text,
	budget = 1.50,
	title = titl,
	options = opts,
	question_timeout_multiplier = 5,
	initial_worker_timeout_in_s = 60,
	image_url = photo_url)

if(estim.isConfident()):
	print("Outcome: Confident Answer")
	print("Answer %s "%(estim.answer))


if(estim.isLowConfidence()):
	print("Outcome: Low Confidence Answer")
	print("Answer %s "%(estim.answer))

if(estim.isOverBudget()):
	print("Outcome: Over Budget")
	print(" need: %f have:%f"%(estim.need, estim.have))
