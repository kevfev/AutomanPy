# AutomanPy
Python bindings for AutoMan. See [AutoMan](https://automan-lang.github.io/). 
This package is currently in development.

### Example Estimate Task:
First, we import the Automan and EstimateOutcome classes from automanpy.automan, then create an adapter. The adapter we pass to the constructor is simply a dictionary with the following required fields:
* access_id - the login id for the crowdsource backend
* access_key - the login access key for the crowdsource backend
* type - the type of crowdsource backend. currently only "mturk" is an accepted type
* any optional arguments for the adapter (currently only "sandbox_mode" for MTurk adapter)

```python
from automanpy.automan import Automan, EstimateOutcome
adapter = {
	"access_id" : "access id here",
	"access_key" : "access key here",
	"sandbox_mode" : "true",
	"type" : "MTurk"
}

```
Here we set `sandbox_mode` to true so that we post the HITs to the development testing sandbox. To run tasks, first create an Automan object. The constructor for Automan objects requires an adapter, and take optional parameters for the RPC server address and port number (default is 'localhost' and 50051).  


When an Automan object is being initialized, if the server_addr is 'localhost' it will start a local AutoMan RPC server as a new process, configured to listen on the provided port number. Only local servers are supported at this time, so this is the only valid value currently. Future functionality will allow users to connect to remote RPC servers. We can now use the Automan object to submit tasks to the crowdsource back-end.

The Automan object allows users to specify a few parameters detailed below:
* 'suppress_output'	- sets the how much output from the RPC server to print to stdout. current valid values are
	* "all" 	- suppress all output
	* "none "	- show all output 

* 'loglevel' 	- sets the the logging level for Automan. valid values are
	* 'debug'	- debug level 
	* 'info' 	- information level (default)
	* 'warn' 	- warnings only
	* 'fatal'	- fatal messages only

```python
a = Automan(adapter, server_addr='localhost',port=50051,suppress_output="none", loglevel='warn')
```
the loglevel is currently set to 'warn', so you will see output generated from the Automan Worker thread in the RPC server.

Each type of task has fields that are required. All tasks require `text` (a text description of the task), and `budget` (desired upper limit of cost of task). The task below has a maximum budget of $1.50 USD, and each worker will have 1 min and 15 seconds (60 seconds + 15 added by default), and the task will only be available for 5 minutes (5 x 60). The desired confidence interval is 90%.

If we have a list of images of parking lots, and we would like to estimate the occupancy, we can do so as follows:

```python
# images to submit with our task
images = ["https://docs.google.com/uc?id=1kpw8sjiZtJwRlVJ3_tYBo26ZcqAeVb5c",
			"https://docs.google.com/uc?id=1Gdlsk24_dAP3YP6eT6Q9A_khVPsMpJzL",
			"https://docs.google.com/uc?id=1tN9E4wpacVpFmTaAkgoUeIyBZek5cBv7"]
estim = a.estimate(text = "How many cars are in this parking lot?",
	budget = 1.50,
	title = "Car Counting",
	confidence = 0.9,
	question_timeout_multiplier = 5,
	initial_worker_timeout_in_s = 60,
	image_url = photo_url)

# spawns 'spawn' number of dummy tasks of same image. Note: each task must have unique text and title for automan to post HIT correctly
task_list = list()
for i in range(len(images)):
	task_list.append(a.estimate(text = "task-%d :Count the number of vehicles in this parking lot"%(i),
							    budget = 1.50,
							    title = "Car Counting-v2-%d"%(i),
							    confidence = 0.9,
								question_timeout_multiplier = 10,
								image_url = images[i]))
```

Here, we simply collect the outcomes in a python list.

We need to wait on the task to resolve it's future before we can print it's result. A better way to handle this will be implemented in the future, but for now the easiest approach would be to wait for each future to resolve, then move on.

```python
#wait fore all futures to resolve
for task in task_list:
	task.done()

for task in task_list:
	task.printOutcome()
```
