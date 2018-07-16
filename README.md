# PyAutoman
This package is currently in development.


### System Requirements
To use this package you must be running Python 2.7 or 3.2+, and Scala 2.11.7+. This package relies on [ScalaPB](https://scalapb.github.io/) and [gRPC](https://grpc.io/). If you use SBT to build this project, all Scala dependencies will be downloaded. To install gRPC for Python (needed for the Python client), follow these [instructions](https://grpc.io/docs/quickstart/python.html).


### How to Build 
To build this project, run sb from the /PyAutoman directory. SBT will also compile the necessary .proto into Scala classes automatically. To generate the the python files needed for the python client, from the /PytAutoman directory, run the following command:

```
python -m grpc_tools.protoc -I src/main/protobuf/ --python_out=src/main/pyautomanlib/core/ --grpc_python_out=src/main/pyautomanlib/core/ src/main/protobuf/automanlib_rpc.proto src/main/protobuf/automanlib_classes.proto
```


### How to Use
First, build this project, then import Automan into your script. (For now, just place in /PyAutoman and import Automan from automan, see example code)


### Example Code 
```
from automan import Automan

adapter = {
	"access_id" : "access key here",
    "access_key" : "secret here",
    "sandbox_mode" : "true",
    "type" : "MTurk"
}
photo_url = "https://docs.google.com/uc?id=1ZQ-oL8qFt2tx_T_-thev2O4dsugVbKI2"

a = Automan(adapter)
est = a.estimate(text = "How full is this parking lot?",
    budget = 1.00,
    title = "Car Counting",
    image_url = photo_url)
a._shutdown()
print("Estimate low: %f high:%f est:%f "%(est.estimateAnswer.low, est.estimateAnswer.high, est.estimateAnswer.est))
````