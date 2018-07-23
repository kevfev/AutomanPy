from automan import Automan

adapter = {
	"access_id" : "access key here",
    "access_key" : "secret here",
    "sandbox_mode" : "true",
    "type" : "MTurk"
}
photo_url = "https://docs.google.com/uc?id=1ZQ-oL8qFt2tx_T_-thev2O4dsugVbKI2"

# launch the automan estimate
estim = a.estimate(text = "How full is this parking lot?",
    budget = 1.00,
    title = "Car Counting",
    image_url = photo_url)

# this is temporary, in future client will automatically handle shutdown
a._shutdown()


if(estim.isEstimate()):
	print("Outcome: Estimate")
	print("Estimate low: %f high:%f est:%f "%(estim.low, estim.high, estim.est))


if(estim.isLowConfidence()):
	print("Outcome: Low Confidence Estimate")
	print("Estimate low: %f high:%f est:%f "%(estim.low, estim.high, estim.est))

if(estim.isOverBudget()):
	print("Outcome: Over Budget")
	print(" need: %f have:%f"%(estim.need, estim.have))