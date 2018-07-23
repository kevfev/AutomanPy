# PyAutoman
See [AutoMan](https://automan-lang.github.io/)
This package is currently in development.


### System Requirements
To use this package you must be running Python 2.7 or 3.2+, and Scala 2.11.7+. This package relies on [ScalaPB](https://scalapb.github.io/) and [gRPC](https://grpc.io/). If you use SBT to build this project, all Scala dependencies will be downloaded. To install gRPC for Python (needed for the Python client), follow these [instructions](https://grpc.io/docs/quickstart/python.html).


### How to Build 
The easiest way to build this project is by using [SBT](https://www.scala-sbt.org/). To build this project, from the /PyAutoman directory, run
```sbt compile pack```
 SBT will also compile the necessary .proto into Scala classes automatically. To generate the the python files needed, from the /PytAutoman directory, run the following command:

```
python -m grpc_tools.protoc -I src/main/protobuf/ --python_out=src/main/pyautoman/pyautoman/core/grpc_gen_classes --grpc_python_out=src/main/pyautoman/pyautoman/core/grpc_gen_classes src/main/protobuf/automanlib_rpc.proto src/main/protobuf/automanlib_classes.proto src/main/protobuf/automanlib_wrappers.proto
```

The python files are already generated and provided (see src/main/pyautomanlib/core/grpc_gen_classes)

### How to Use
To run tasks, first create an Automan object. Automan objects require an adapter, and take optional parameters for the RPC server address and port number (default is 'localhost' and 50051).  The adapter we pass to the constructor is simply a dictionary with the following required fields:
* access_id
* access_key
* type

First, import the Automan class:

```
Python 2.7.15 |Anaconda, Inc.| (default, May  1 2018, 18:37:05) 
[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> adapter = {
...     "access_id" : "access id here",
...     "access_key" : "access key here",
...     "sandbox_mode" : "true",
...     "type" : "MTurk"
... }

```

When the Automan object is initialized, if the address is 'localhost' it will start a local AutoMan RPC server as a new process configured to listen on the provided port number. Future functionality will allow users to connect to remove RPC servers. We can now use the Automan object to submit tasks to the crowdsource back-end. Currently, only the `estimate` function of Automan is available. See example code for usage.

Each type of task has fields that are required. All tasks require `text` (a text description of the task), `image_url` and `budget` (desired upper limit of cost of task). We specify the tasks we would like AutoMan to carry out, and result computation blocks and returns either when the question has timed out and budget is exceeded (resulting in a low confidence or overbudget outcome, more in this later) or the desired confidence level has been met and the estimate is return.

```
>>> a = Automan(adapter, server_addr='localhost',port=50051)
python client is starting server...
Server Started on port 50051 ...
>>> photo_url = "https://docs.google.com/uc?id=1ZQ-oL8qFt2tx_T_-thev2O4dsugVbKI2"
>>> estim = a.estimate(text = "How full is this parking lot?",budget = 1.00, title = "Car Counting",image_url = photo_url)
```
To print the result of the task.
```
estim.printOutcome()
>>> estim.printOutcome()
Outcome: Low Confidence Estimate
Estimate low: 62.000000 high:62.000000 est:62.000000
```

The outcome can be either:
*Estimate
*Low Confidence estimate
*Overbudget
`printOutcome()` is a convenient way to print the result, but see the example code for further usage. 


### Example Code 
```
from pyautoman.automan import Automan, EstimateOutcome

# make mechanical turk adapter
adapter = {
	"access_id" : "access id here",
    "access_key" : "access key here",
    "sandbox_mode" : "true",
    "type" : "MTurk"
}

# make AutoMan object 
a = Automan(adapter, server_addr='localhost',port=50051)

# submit estimation job to AutoMan
estim = a.estimate(text = "How full is this parking lot?",
    budget = 1.00,
    title = "Car Counting",
    image_url = photo_url)

# this is temporary, in future client will automatically handle shutdown
a._shutdown()

# The estimation may be a confident estimate, a low confidence estimate
# or the task did not complete because it went over budget
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
You can run the code on MTurk with the 'sandbox_mode' option set to 'true' and submit
a response (need to create requester developer and worker sandbox accounts) to see output.
Here is what the output would look like if a single worker submitted a response of 62.
Output:
```
Outcome: Low Confidence Estimate
Estimate low: 62.000000 high:62.000000 est:62.000000 
```