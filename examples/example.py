from pyautoman.automan import Automan, EstimateOutcome

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
# 	"all" 	- suppress all output
# 	"none "	- show all output 
a = Automan(adapter, server_addr='localhost',port=50051,suppress_output="none")

estim = a.estimate(text = "How many cars are in this parking lot?",
	budget = 6.00,
	title = "Car Counting",
	confidence_int = 10,
	image_url = photo_url)

if(estim.isConfident()):
	print("Outcome: Estimate")
	print("Estimate low: %f high:%f est:%f "%(estim.low, estim.high, estim.est))


if(estim.isLowConfidence()):
	print("Outcome: Low Confidence Estimate")
	print("Estimate low: %f high:%f est:%f "%(estim.low, estim.high, estim.est))

if(estim.isOverBudget()):
	print("Outcome: Over Budget")
	print(" need: %f have:%f"%(estim.need, estim.have))

# this is temporary, in future client will automatically handle shutdown
# to be safe, only call _shutdown() after the future has resolved,
# or else the server will kill itself before the computation is finished 
a._shutdown()