# AutomanPy
Python bindings for AutoMan. See [AutoMan](https://automan-lang.github.io/). 
This package is currently in development.

## API
### AutoMan Class 
#### Constructor
```python
Automan(self, adapter, server_addr = 'localhost', port = 50051, suppress_output = 'all', loglevel='info')
```
##### *Description* : 
Provides AutoMan's estimate functionality. Uses the crowdsource backend to obtain a quality-controlled  
estimate of a single real value.     
##### *Arguments*

* **adapter** 			- a dictionary storing adapter credentials to use to connect to the crowdsource backend. Must contain necessary adapter fields
* **server_addr**		- the string hostname address of the gRPC Automan server to connect to
* **port** 				- the port number to connect to the gRPC Automan server
* **supress_output**	- the level of output to show from the gRPC Automan server. "none" displays all output, "all" supresses all output from server
* **loglevel** 			- Specifies the AutoMan worker log level, for setting the level of output directly from AutoMan. values
	* 'debug' 	- debug level 
	* 'info' 	- information level 
	* 'warn'	- warnings only
	* 'fatal' 	- fatal messages only (default)

##### *Returns*: `automanpy.automan.Automan`
#### Functions
##### Automan.estimate
```
Automan.estimate(self, text, budget, image_url ="", title = "", confidence = 0.95, confidence_int = -1, 
		img_alt_txt = "", sample_size = -1,dont_reject = True, pay_all_on_failure = True, dry_run = False,
		wage = 11.00, max_value = sys.float_info.max, min_value = sys.float_info.min, 
		question_timeout_multiplier = 500, initial_worker_timeout_in_s = 30)
```
##### *Description* : 
Provides AutoMan's estimate functionality. Uses the crowdsource backend to obtain a quality-controlled  
estimate of a single real value.     
**_Note_**: Be careful when setting 'question_timeout_multiplier' and 'initial_worker_timeout_in_s' in tasks.  
Setting too low can cause the question to timeout too soon and result in failure to get results.  
Use, at minimum, values 30 or higher for `question_timeout_multiplier` and 30 or higher for `initial_worker_timeout_in_s`. 
##### *Arguments*
* **text** 							- the text description of the task to display to the worker (required)
* **budget** 						- the threshold cost for the task (required)
* **image_url**  					- an image url to be associated with the task
* **title**   						- title of the task, displayed to worker
* **confidence** 					- desired confidence level
* **confidence_int** 				- desired confidence interval
* **img_alt_txt** 					- alternative image text, for generated webpage displayed to worker
* **sample_size** 					- desired sample size, default of -1 indicates to use default samp. size of 30
* **dont_reject** 					- indicate whether to accept all answers automatically or not (?)
* **pay_all_on_failure** 			- indicate whether to pay all workers on task failure or not (?)
* **dry_run** 						- indicate whether to do a dry run or not
* **wage** 							- minimum wage to pay the worker, in USD/hr
* **max_value** 					- min value for dimension being estimated
* **min_value** 					- max value for dimension being estimated
* **question_timeout_multiplier** 	- multiplier to calculate question timeout on MTurk. Question timeout = question_timeout_multiplier * initial_worker_timeout_in_s
* **initial_worker_timeout_in_s** 	- timeout in seconds for the worker thread in the RPC server 

##### *Returns* : `automanpy.automan.EstimateOutcome`  

##### Automan.radio
```
Automan.radio(self, text=None, budget=None, options=None, confidence = 0.95, dont_reject = True, 
			dry_run = False,initial_worker_timeout_in_s = 30, img_alt_txt = "",image_url="", 
			pay_all_on_failure = True, question_timeout_multiplier = 500, title = "",wage = 11.00)
```
##### *Description* : 
Provides AutoMan's radio functionality. Uses the crowdsource backend to obtain a quality-controlled  
answer to a radio choice task (multiple-choice single-answer).     
**_Note_**: Be careful when setting 'question_timeout_multiplier' and 'initial_worker_timeout_in_s' in tasks.  
Setting too low can cause the question to timeout too soon and result in failure to get results.  
Use, at minimum, values 30 or higher for `question_timeout_multiplier` and 30 or higher for `initial_worker_timeout_in_s`. 
choicename, choice, and url in the options argument dict are all strings. Note that you cannot mix the different formats
##### *Arguments*
* **text** 							- the text description of the task to display to the worker (required)
* **budget** 						- the threshold cost for the task (required)
* **options**						- A dictionary of string values of possible of possible radio choices (choicename -> (choice) or choicename -> (choice, url)) (required)
* **image_url**  					- an image url to be associated with the task
* **title**   						- title of the task, displayed to worker
* **confidence** 					- desired confidence level
* **img_alt_txt** 					- alternative image text, for generated webpage displayed to worker
* **sample_size** 					- desired sample size, default of -1 indicates to use default samp. size of 30
* **dont_reject** 					- indicate whether to accept all answers automatically or not (?)
* **pay_all_on_failure** 			- indicate whether to pay all workers on task failure or not (?)
* **dry_run** 						- indicate whether to do a dry run or not
* **wage** 							- minimum wage to pay the worker, in USD/hr
* **question_timeout_multiplier** 	- multiplier to calculate question timeout on MTurk. Question timeout = question_timeout_multiplier * initial_worker_timeout_in_s
* **initial_worker_timeout_in_s** 	- timeout in seconds for the worker thread in the RPC server 

##### *Returns* : `automanpy.automan.RadioOutcome`  

### Outcome Class
##### *Description* : 
This class as an interface for the outcome of the task. Attributes in this class are common attributes of all outcome types for various tasks(i.e. conf, cost, need, have), initially set to NaN so that they cannot used. Concrete implementations of this class are detailed below.
##### *Attributes*
* **cost**	- the cost to complete the task, set to NaN intially
* **conf** 	- the confidence interval of the outcome, set to NaN intially  
* **need** 	- the amount needed for AutoMan to continue attempting to a confident answer
* **have** 	- the current amount budgeted for the task  

#### Outcome.isConfident()
##### *Description* : 
Indicates if the outcome of the task is a confident result
##### *Returns* : `boolean` - True if the outcome met the desired confidence level and interval, False otherwise  
 
#### Outcome.isLowConfidence()
##### *Description* : 
Indicates if the outcome of the task is a low confidence result  
##### *Returns* : `boolean` - True if the outcome was a low confidence estimate, False otherwise  
 
#### Outcome.isOverBudget()
##### *Description* : 
Indicates if the outcome of the task is an over budget result  
##### *Returns* : `boolean` - True if the outcome was over budget, False otherwise  

#### Outcome.printOutcome()
##### *Description* : 
Prints the outcome of the estimate to stdout
##### *Returns* : `None` 

#### Outcome.isDone()
##### *Description* : 
Indicates if the call for this task has completed or not. This call does not block 
##### *Returns* : `boolean` - True if the outcome has resolved (either "CONFIDENT", "LOW_CONFIDENCE", or "OVERBUDGET")

#### Outcome.done()
##### *Description* : 
This function waits for the function call for this task to complete (waits for future to resolve). This call blocks.
##### *Returns* : `None`

### EstimateOutcome Class
##### *Description* : 
EstimateOutcomes are the result of estimate tasks. This object contains a Future, representing the outcome of the task. Value attributes in this class (e.g. high, est, cost, need, etc) are initially set to NaN so that they cannot used, until the future has resolved to a case where those values are valid (e.g., if the outcome_type was `OVERBUDGET` then `need` and `have` are the only valid attributes). To ensure that the future is always resolved first and the respective attributes are initialized, always use attributes of an EstimateOutcome in conditonal blocks where they exist, using the appropriate methods below 
**_Note_**: Instances of this class will always be created for the user. This class will never need to be instantiated manually.  
##### *Attributes*
For `Confident` and `LowConfidence` outcomes:
* **high** 	- the high value of the confidence interval, set to NaN intially
* **low** 	- the low value of the confidence interval, set to NaN intially
* **est** 	- the estimated value, set to NaN intially
* **cost**	- the cost to complete the task, set to NaN intially
* **conf** 	- the confidence interval of the estimate, set to NaN intially  

For `OverBudget` outcomes:  
* **need** 	- the amount needed for AutoMan to continue attempting to obtain an estimate
* **have** 	- the current amount budgeted for the task  

#### EstimateOutcome.isConfident()
##### *Description* : 
Indicates if the outcome of the task is a confident estimate  
##### *Returns* : `boolean` - True if the outcome met the desired confidence level and interval, False otherwise  
 
#### EstimateOutcome.isLowConfidence()
##### *Description* : 
Indicates if the outcome of the task is a low confidence estimate  
##### *Returns* : `boolean` - True if the outcome was a low confidence estimate, False otherwise  
 
#### EstimateOutcome.isOverBudget()
##### *Description* : 
Indicates if the outcome of the task is over budget or not  
##### *Returns* : `boolean` - True if the outcome was over budget, False otherwise  

#### EstimateOutcome.printOutcome()
##### *Description* : 
Prints the outcome of the estimate to stdout
##### *Returns* : `None` 

#### EstimateOutcome.isDone()
##### *Description* : 
Indicates if the call for this task has completed or not. This call does not block 
##### *Returns* : `boolean` - True if the estimate has returned (either "CONFIDENT", "LOW_CONFIDENCE", or "OVERBUDGET")

#### EstimateOutcome.done()
##### *Description* : 
This function waits for the function call for this task to complete (waits for future to resolve). This call blocks.
##### *Returns* : `None`

### RadioOutcome Class
##### *Description* : 
RadioOutcomes are the result of radio tasks. This object contains a Future, representing the outcome of the task. Value attributes in this class (e.g. high, est, cost, need, etc) are initially set to NaN so that they cannot used, until the future has resolved to a case where those values are valid (e.g., if the outcome_type was `OVERBUDGET` then `need` and `have` are the only valid attributes). To ensure that the future is always resolved first and the respective attributes are initialized, always use attributes of an EstimateOutcome in conditonal blocks using the appropriate methods below to ensure values are valid
**_Note_**: Instances of this class will always be created for the user. This class will never need to be instantiated manually.  
##### *Attributes*
For `Confident` and `LowConfidence` outcomes:
* **answer** 	-the crowdsourced radio response, set to None intially
* **cost**	- the cost to complete the task, set to NaN intially
* **conf** 	- the confidence interval of the estimate, set to NaN intially  

For `OverBudget` outcomes:  
* **need** 	- the amount needed for AutoMan to continue attempting to obtain an estimate
* **have** 	- the current amount budgeted for the task  

#### RadioOutcome.isConfident()
##### *Description* : 
Indicates if the outcome of the task is a confident estimate  
##### *Returns* : `boolean` - True if the outcome met the desired confidence level and interval, False otherwise  
 
#### RadioOutcome.isLowConfidence()
##### *Description* : 
Indicates if the outcome of the task is a low confidence estimate  
##### *Returns* : `boolean` - True if the outcome was a low confidence answer, False otherwise  
 
#### RadioOutcome.isOverBudget()
##### *Description* : 
Indicates if the outcome of the task is over budget or not  
##### *Returns* : `boolean` - True if the outcome was over budget, False otherwise  

#### RadioOutcome.printOutcome()
##### *Description* : 
Prints the answer to stdout
##### *Returns* : `None` 

#### RadioOutcome.isDone()
##### *Description* : 
Indicates if the call for this task has completed or not. This call does not block 
##### *Returns* : `boolean` - True if the estimate has returned (either "CONFIDENT", "LOW_CONFIDENCE", or "OVERBUDGET")

#### RadioOutcome.done()
##### *Description* : 
This function waits for the function call for this task to complete (waits for future to resolve). This call blocks.
##### *Returns* : `None`