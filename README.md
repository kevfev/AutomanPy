# PyAutoman
This package is currently in development.


### System Requirements
To use this package you must be running Python 2.7 or 3.2+, and Scala 2.11.7+. This package relies on [ScalaPB](https://scalapb.github.io/) and [gRPC](https://grpc.io/). If you use SBT to build this project, all Scala dependencies will be downloaded. To install gRPC for Python (needed for the Python client), follow these [instructions](https://grpc.io/docs/quickstart/python.html).


### How to Build 
To build this project, run sbt from the /PyAutoman directory, then compile using the "compile" command of SBT. SBT will also compile the necessary .proto into Scala classes automatically. To generate the the python files needed for the python client, from the /PytAutoman directory, run the following command:

```
python -m grpc_tools.protoc -I src/main/protobuf/ --python_out=src/main/pyautomanlib/core/ --grpc_python_out=src/main/pyautomanlib/core/ src/main/protobuf/automanlib_rpc.proto src/main/protobuf/automanlib_classes.proto
```
The python files are already generated and provided (see src/main/pyautomanlib/core/)

### How to Use
First, build this project, then import Automan into your script. (For now, just place in /PyAutoman and import Automan from automan, see example code). For now, the gRPC server that services the Automan request must be started manually using sbt. From the /PyAutoman, launch sbt, then start the server using the run command, supplying a port number. The default port is 50051. See below for an example.

```
user:PyAutoman user$ sbt
... (sbt will print to console here)
sbt:PyAutoman>
sbt:PyAutoman> run 50051
[info] Running automanlib.EstimationPrototypeServicer 
Server Started on port 50051 ...
```

Now, we can run python scripts that can connect to this local automan server to run automan jobs. First, we will need to create an adapter. Currently, only Mechnical Turk adapters are supported. To create an adapter, we must supply an access_id, access_key, any additional options for the adapter e.g. sandbox mode(need to add more options later), and the type of the adapter. Then, we pass the adapter and 

```
adapter = {
	"access_id" : "access key here",
    "access_key" : "secret here",
    "sandbox_mode" : "true",
    "type" : "MTurk"
}
a = Automan(adapter)
```

We can now use the Automan object to submit tasks to the crowdsource back-end. Currently, only the `estimate` function of Automan is available. See example code for usage.


### Example Code 
```
from automan import Automan

adapter = {
	"access_id" : "access key here",
    "access_key" : "secret here",
    "sandbox_mode" : "true",
    "type" : "MTurk"
}
a = Automan(adapter, server_addr='localhost',port=50051)
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
````
A single response was submitted for this query, generating a Low Confidence estimate.
Output:
```
Outcome: Low Confidence Estimate
Estimate low: 62.000000 high:62.000000 est:62.000000 
```