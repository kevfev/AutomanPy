# AutomanPy
Python bindings for AutoMan. See [AutoMan](https://automan-lang.github.io/). 
This package is currently in development.

### System Requirements
To use this package you must be running Python 2.7.15 or 3.2+,Java 8, and Scala 2.11.7+. This package relies on [ScalaPB](https://scalapb.github.io/) and [gRPC](https://grpc.io/). If you use SBT to build this project, all Scala dependencies will be downloaded. To install gRPC for Python (needed for the Python client), follow these [instructions](https://grpc.io/docs/quickstart/python.html).


### How to Install
Use pip to install AutoManPy. 
```
pip install automanpy
```
This software package is currently in development, and will be updated regularly for bug fixes, etc. 
If you want to upgrade, or force the installation of the latest version, use '--no-cache-dir' and '--upgrade'
```
pip install --no-cache-dir automanpy --upgrade
```

### How to Build Source
The easiest way to build this project is by using [SBT](https://www.scala-sbt.org/).To build the source automatically, you can run `./buildproject.sh` located in the root directory. This relies on sbt being installed.  
To build this project manually, from the /AutomanPy directory, run
```
sbt clean compile pack
```
SBT will also compile the necessary .proto into Scala classes automatically. To generate the the python files needed, `grpcio-tools` and `googleapis-common-protos` need to be installed. These python dependencies are automatically installed by pip if this package is installed from the provided tarball (). To install the necessary packages manually, run the following two commands:
```
pip install grpcio-tools
pip install googleapis-common-protos
```
To use gRPC generate the python files needed for interacting with the RPC service, from the /AutomanPy directory, run the following command:

```
python -m grpc_tools.protoc -I src/main/protobuf/ --python_out=src/main/automanpy/automanpy/core/grpc_gen_classes/ --grpc_python_out=src/main/automanpy/automanpy/core/grpc_gen_classes src/main/protobuf/core/grpc_gen_classes/automanlib_rpc.proto src/main/protobuf/core/grpc_gen_classes/automanlib_classes.proto src/main/protobuf/core/grpc_gen_classes/automanlib_wrappers.proto
```

Move the files compiled by sbt into the correct directory by copying them:
```
cp -r target/pack/ src/main/automanpy/automanpy/core/rpc/server/
```

Then change to the directory containing setup.py and run it from there:
```
cd src/main/automanpy/
python setup.py clean sdist
```

### How to Use
To run tasks, first create an Automan object. The constructor for Automan objects requires an adapter, and take optional parameters for the RPC server address and port number (default is 'localhost' and 50051).  The adapter we pass to the constructor is simply a dictionary with the following required fields:
* access_id - the login id for the crowdsource backend
* access_key - the login access key for the crowdsource backend
* type - the type of crowdsource backend. currently only "mturk" is an accepted type
* any optional arguments for the adapter (currently only "sandbox_mode" for MTurk adapter)

First, import the Automan and EstimateOutcome classes from automanpy.automan, then create an adapter

```python
Python 2.7.15 |Anaconda, Inc.| (default, May  1 2018, 18:37:05) 
[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from automanpy.automan import Automan, EstimateOutcome
>>> adapter = {
...     "access_id" : "access id here",
...     "access_key" : "access key here",
...     "sandbox_mode" : "true",
...     "type" : "MTurk"
... }

```

When an Automan object is being initialized, if the server_addr is 'localhost' it will start a local AutoMan RPC server as a new process, configured to listen on the provided port number. Future functionality will allow users to connect to remote RPC servers. We can now use the Automan object to submit tasks to the crowdsource back-end. Currently, only the `estimate` function of Automan is available. See example code for usage.

```python
>>> a = Automan(adapter, server_addr='localhost',port=50051)
python client is starting server...
Server Started on port 50051 ...
>>> photo_url = "https://docs.google.com/uc?id=1ZQ-oL8qFt2tx_T_-thev2O4dsugVbKI2"
>>> estim = a.estimate(text = "How many cars are in this parking lot?",budget = 6.00, title = "Car Counting",image_url = photo_url)
```

Each type of task has fields that are required. All tasks require `text` (a text description of the task), and `budget` (desired upper limit of cost of task). We specify the tasks we would like AutoMan to carry out, and either when the question has timed out and budget is exceeded (resulting in a low confidence or overbudget outcome respectively) or the desired confidence level has been met.  

The outcome can be either:
* Confident estimate
* Low Confidence estimate
* Overbudget  

If the task went overbudget, the `need` and `have` fields of the returned EstimateOutcome are initialized, otherwise `high`, `low`, `est`, `cost`, and `conf` are initialized. AutomanPy uses gRPC's implementation of Futures. To ensure the future is resolved before values are accessed, only try to access respective values within code blocks that ensure those values are set. See methods `isConfident()`, `isLowConfidence()`, and `isOverBudget()` below. To see more example code, and an example for posting multiple tasks, see AutomanPy/examples


To simply print the result of the task, use `printOutcome()`.
```python
estim.printOutcome()
>>> estim.printOutcome()
Outcome: Low Confidence Estimate
Estimate low: 62.000000 high:62.000000 est:62.000000
```

### Example Code 
See example usage for submitting single and multiple estimate tasks in [`examples/`](https://github.com/kevfev/AutomanPy/tree/master/examples)

### API
See the API under [`examples/`](https://github.com/kevfev/AutomanPy/tree/master/examples)


