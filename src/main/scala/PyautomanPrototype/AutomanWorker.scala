package pyautomanlib;
import edu.umass.cs.automan.adapters.mturk.DSL._;
import edu.umass.cs.automan.core.question.confidence.ConfidenceInterval;
import edu.umass.cs.automan.core.logging.{LogLevel, LogLevelFatal, LogLevelInfo, LogLevelWarn, LogLevelDebug}
import edu.umass.cs.automan.core.logging.LogConfig.LogConfig
import edu.umass.cs.automan.core.MagicNumbers;
import automanlib_rpc.AutomanTask.TaskType;
import automanlib_rpc._;
import automanlib_classes._;
import automanlib_wrappers._;
import scala.concurrent.{ ExecutionContext, Future };
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.AbstractQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

class AutomanWorker(worker_id: String, adptr: AdapterCredentials, workQueue: AbstractQueue[(String, AutomanTask.TaskType)], 
					resultMap: ConcurrentMap[String, AnyRef], stopWorker: AtomicBoolean) extends Runnable{
	val workerID: String = worker_id;
	val adapter: AdapterCredentials = adptr;
	val queue: AbstractQueue[(String, AutomanTask.TaskType)] = workQueue;
	val map: ConcurrentMap[String, AnyRef] = resultMap;

	var ll = adptr.logLevel;
	var loglevel : LogLevel = LogLevelInfo()
	// 1 is same as LogLevelInfo, default option
 	ll match {
		case 0 => loglevel = LogLevelDebug()
		case 2 => loglevel = LogLevelWarn()
		case 3 => loglevel = LogLevelFatal()
		case _ => loglevel = LogLevelInfo()

	}

	var lg = adptr.logging;
	var log: LogConfig = LogConfig.TRACE_MEMOIZE;
 	lg match {
 		case 0 => log = LogConfig.TRACE_MEMOIZE
		case 1 => log = LogConfig.NO_LOGGING
		case 2 => log = LogConfig.TRACE
		case 3 => log = LogConfig.TRACE_VERBOSE
		case 4 => log = LogConfig.TRACE_MEMOIZE_VERBOSE
		case _ => log = LogConfig.TRACE_MEMOIZE

	}

	implicit val mt = mturk (access_key_id = adptr.accessId,
							secret_access_key = adptr.accessKey,
							log_verbosity = loglevel,
							logging = log,
							sandbox_mode = adptr.adapterOptions("sandbox_mode").toBoolean)

	Thread.currentThread().setName("RPC-AutoMan-Worker");

	/** check if there is another job
	*
	*  @return Boolean,return true if there is a new task submitted, else return false
	*							
	*/
	def newTaskAvail() : Boolean = {
		// check if there 
		if (workQueue.peek() == null){
			return false;
		}	
		return true;
	}

	/** Launches an AutoMan task and returns the future outcome
	*
	*  @param task - the user submitted task to be run
	*  @return Future outcome, returned by AutoMan
	*							
	*/
	def launchTask(taskID: String, task: AnyRef) : Unit = {
		// run automan job
		task match {
			case TaskType.Estimate(etask)		=> 	launchEstimateTask(taskID=taskID, task=etask.getTask);
			case TaskType.Multiestimate(metask) => 	launchMultiEstimateTask(taskID=taskID, task=metask.getTask);
			case TaskType.Freetext(frtask)		=>	launchFreetextTask(taskID=taskID, task=frtask.getTask);
			case TaskType.FreetextDist(frdtask) =>	launchFreetextDistTask(taskID=taskID, task=frdtask.getTask);
			case TaskType.Radio(rtask) 			=>	launchRadioTask(taskID=taskID, task=rtask.getTask);
			case TaskType.RadioDist(rdtask) 	=>	launchRadioDistTask(taskID=taskID, task=rdtask.getTask);
			case TaskType.Checkbox(chtask) 		=>	launchCheckboxTask(taskID=taskID, task=chtask.getTask);
			case TaskType.CheckboxDist(chdtask) =>	launchCheckboxDistTask(taskID=taskID, task=chdtask.getTask);
			case TaskType.Empty					=>	println("ERROR: Unknown type of task received by RPC AutoMan worker. Server generated bad task");
													throw new Exception("Task is empty! this exception should be handled by RPC server")
		}
	}

	/** Adds the future outcome to the map so that the thread that submitted task can 
	*	access the result. If a duplicate key was randomly generated and somehow was not 
	*	regenerated, this method should throw an exception
	*
	*  	@param resultKey - the key associated with this outcome
	*  	@param outcome - the future outcome
	*							
	*/
	def addToResultMap(taskID: String, outcome: AnyRef) : Unit = {
		// add future to map
		resultMap.put(taskID, outcome);
	}

	/** Makes options from OptionsTuple for tasks that require option choices 
	*
	*  	@param options - the OptionsTuple to create options for
	*	@return a List of options
	*					
	*/
	def makeOptions(options: Option[OptionsTuple]) : List[AnyRef] = {
		var opts: OptionsTuple = options.getOrElse(throw new Exception("options not specified for task, this should throw an exception!"))
		if(opts.tupleType.isSingle){
			return opts.single.map{ case(choice_name,name) => choice(Symbol(choice_name), name)}.toList
		}
		if(opts.tupleType.isDouble){	 
			return opts.double.map{ case(choice_name,d_tup) => choice(Symbol(choice_name), d_tup.name, d_tup.url)}.toList
		}
		if(opts.tupleType.isUnknown){
			throw new Exception("options not specified for task, this should throw an exception!")
		}
		return {(Symbol("n/a") -> "n/a")}.toList

	}

	/** Main loops of worker thread. Until server stops worker, 
	*	fetch task (or wait for one), then launch task
	*	and add the future outcome to the outcome map
	*
	*							
	*/
	def run(){
		while(!stopWorker.get){
			if(newTaskAvail()){
				val taskTuple = workQueue.poll();
				val taskID: String = taskTuple._1;
				val task: AutomanTask.TaskType = taskTuple._2;
				launchTask(taskID, task);
			}
			else
			{
				Thread.sleep(5000);
			}
			
		}
	}

	/**  method for launching an estimation task
	*	@param taskID - ID of submitted task
	*  	@param task - submitted task
	*  	@return returns Future outcome returned by AutoMan
	*							
	*/
	def launchEstimateTask(taskID: String, task : Task) : Unit = {
		//TODO
		//MAKE RETURN TYPE RESULT OR THROW EXCEPTIONS
		var ci : ConfidenceInterval = UnconstrainedCI();
		if (task.confidenceInt > 0) {
			ci = SymmetricCI(task.confidenceInt)
		}
		val outcome = estimate(text =task.text, 
								budget = task.budget, 
								image_url =task.imageUrl,
								image_alt_text =task.imgAltTxt,
								title = task.title, 
								default_sample_size = task.sampleSize,
								pay_all_on_failure = task.payAllOnFailure,
								dont_reject  = task.dontReject,
								dry_run  = task.dryRun,
								wage = task.wage,
								confidence = task.confidence, 
								confidence_interval = ci,
								max_value = task.maxValue,
								min_value = task.minValue,
								initial_worker_timeout_in_s = task.initialWorkerTimeoutInS,
								question_timeout_multiplier = task.questionTimeoutMultiplier);
		addToResultMap(taskID,outcome);
	}

	/** wrapper method for launching a multiestimation task
	*
	*	@param taskID - ID of submitted task
	*  	@param task - submitted task
	*  	@return returns Future outcome returned by AutoMan
	*							
	*/
	def launchMultiEstimateTask(taskID: String, task : Task) : Unit = {
		//TODO
		//MAKE RETURN TYPE RESULT OR THROW EXCEPTIONS
	}


	/** wrapper method for launching a freetext task
	*
	*	@param taskID - ID of submitted task
	*  	@param task - submitted task
	*  	@return returns Future outcome returned by AutoMan
	*							
	*/
	def launchFreetextTask(taskID: String, task : Task) : Unit = {
		//TODO
		//MAKE RETURN TYPE RESULT OR THROW EXCEPTIONS
	}

	/** wrapper method for launching a freetext distribution task
	*
	*	@param taskID - ID of submitted task
	*  	@param task - submitted task
	*  	@return returns Future outcome returned by AutoMan
	*							
	*/
	def launchFreetextDistTask(taskID: String, task : Task) : Unit = {
		//TODO
		//MAKE RETURN TYPE RESULT OR THROW EXCEPTIONS
	}

	/** wrapper method for launching a radio task
	*
	*	@param taskID - ID of submitted task
	*  	@param task - submitted task
	*  	@return returns Future outcome returned by AutoMan
	*							
	*/
	def launchRadioTask(taskID: String, task : Task) : Unit = {
		//TODO
		//MAKE RETURN TYPE RESULT OR THROW EXCEPTIONS
		val opts = makeOptions(task.options)
		val outcome = radio(text =task.text, 
								budget = task.budget, 
								options = opts,
								image_url =task.imageUrl,
								image_alt_text =task.imgAltTxt,
								title = task.title, 
								pay_all_on_failure = task.payAllOnFailure,
								dont_reject  = task.dontReject,
								dry_run  = task.dryRun,
								wage = task.wage,
								confidence = task.confidence, 
								initial_worker_timeout_in_s = task.initialWorkerTimeoutInS,
								question_timeout_multiplier = task.questionTimeoutMultiplier);
		addToResultMap(taskID,outcome);
	}

	/** wrapper method for launching radio distribution task
	*
	*	@param taskID - ID of submitted task
	*  	@param task - submitted task
	*  	@return returns Future outcome returned by AutoMan
	*							
	*/
	def launchRadioDistTask(taskID: String, task : Task) : Unit = {
		//TODO
		//MAKE RETURN TYPE RESULT OR THROW EXCEPTIONS
	}

	/** wrapper method for launching a checkbox task
	*
	*	@param taskID - ID of submitted task
	*  	@param task - submitted task
	*  	@return returns Future outcome returned by AutoMan
	*							
	*/
	def launchCheckboxTask(taskID: String, task : Task) : Unit = {
		//TODO
		//MAKE RETURN TYPE RESULT OR THROW EXCEPTIONS
	}

	/** wrapper method for launching checkbox distribution tasks
	*
	*	@param taskID - ID of submitted task
	*  	@param task - submitted task
	*  	@return returns Future outcome returned by AutoMan
	*							
	*/
	def launchCheckboxDistTask(taskID: String, task : Task) : Unit = {
		//TODO
		//MAKE RETURN TYPE RESULT OR THROW EXCEPTIONS

	}
}
