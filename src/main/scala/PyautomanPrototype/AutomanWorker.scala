package pyautomanlib;
import edu.umass.cs.automan.adapters.mturk.DSL._;
import edu.umass.cs.automan.core.question.confidence.ConfidenceInterval;
import edu.umass.cs.automan.core.logging.{LogLevel, LogLevelFatal, LogLevelInfo, LogLevelWarn, LogLevelDebug}
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
 	ll match {
		case 0 => loglevel = LogLevelDebug()
		case 2 => loglevel = LogLevelWarn()
		case 3 => loglevel = LogLevelFatal()
		case _ => loglevel = LogLevelInfo()

	}

	implicit val mt = mturk (access_key_id = adptr.accessId,
							secret_access_key = adptr.accessKey,
							log_verbosity = loglevel,
							sandbox_mode = adptr.adapterOptions("sandbox_mode").toBoolean)


	/** check if there is another job
	*
	*  @param * - estimation task paramaters
	*  @return Future outcome, returned by AutoMan
	*							
	*/
	def newTaskAvail() : Boolean = {
		// check if there 
		if (workQueue.peek() == null){
			Thread.sleep(5000);
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
		}
	}

	/** Adds the future outcome to the map so that the thread that submitted task can 
	*	access the result. If a duplicate key was randomly generated and somehow was not 
	*	regenerated, this method should throw an exception
	*
	*  @param resultKey - the key associated with this outcome
	*  @param outcome - the future outcome
	*							
	*/
	def addToResultMap(taskID: String, outcome: AnyRef) : Unit = {
		// add future to map
		resultMap.put(taskID, outcome);
	}

	/** Main loops of worker thread. Fetch task (or wait for one), then launch task
	*	and add the future outcome to the outcome map
	*
	*							
	*/
	def run(){
		while(!stopWorker.get){
			if(newTaskAvail()){
				val taskTup = workQueue.poll();
				val taskID: String = taskTup._1;
				val task: AutomanTask.TaskType = taskTup._2;
				launchTask(taskID, task);
			}
			
		}
	}

	/**  method for launching and estimation task
	*
	*  @param task - submitted task
	*  @return returns Future outcome returned by AutoMan
	*							
	*/
	def launchEstimateTask(taskID: String, task : Task) : Unit = {

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

	/** wrapper method for launching and estimation task
	*
	*  @param task - submitted task
	*  @return returns Future outcome returned by AutoMan
	*							
	*/
	def launchMultiEstimateTask(taskID: String, task : Task) : Unit = {
		var ci : ConfidenceInterval = UnconstrainedCI()
		if (task.confidenceInt > 0) {
			ci = SymmetricCI(task.confidenceInt)
		}

	}


	/** wrapper method for launching and estimation task
	*
	*  @param task - submitted task
	*  @return returns Future outcome returned by AutoMan
	*							
	*/
	def launchFreetextTask(taskID: String, task : Task) : Unit = {
		var ci : ConfidenceInterval = UnconstrainedCI()
		if (task.confidenceInt > 0) {
			ci = SymmetricCI(task.confidenceInt)
		}

	}

	/** wrapper method for launching and estimation task
	*
	*  @param task - submitted task
	*  @return returns Future outcome returned by AutoMan
	*							
	*/
	def launchFreetextDistTask(taskID: String, task : Task) : Unit = {
		var ci : ConfidenceInterval = UnconstrainedCI()
		if (task.confidenceInt > 0) {
			ci = SymmetricCI(task.confidenceInt)
		}

	}

	/** wrapper method for launching radio task
	*
	*  @param task - submitted task
	*  @return returns Future outcome returned by AutoMan
	*							
	*/
	def launchRadioTask(taskID: String, task : Task) : Unit = {
		var ci : ConfidenceInterval = UnconstrainedCI()
		if (task.confidenceInt > 0) {
			ci = SymmetricCI(task.confidenceInt)
		}

	}

	/** wrapper method for launching radio distribution task
	*
	*  @param task - submitted task
	*  @return returns Future outcome returned by AutoMan
	*							
	*/
	def launchRadioDistTask(taskID: String, task : Task) : Unit = {
		var ci : ConfidenceInterval = UnconstrainedCI()
		if (task.confidenceInt > 0) {
			ci = SymmetricCI(task.confidenceInt)
		}

	}

	/** wrapper method for launching checkbox tasks
	*
	*  @param task - submitted task
	*  @return returns Future outcome returned by AutoMan
	*							
	*/
	def launchCheckboxTask(taskID: String, task : Task) : Unit = {
		var ci : ConfidenceInterval = UnconstrainedCI()
		if (task.confidenceInt > 0) {
			ci = SymmetricCI(task.confidenceInt)
		}

	}

	/** wrapper method for launching checkbox distribution tasks
	*
	*  @param task - submitted task
	*  @return returns Future outcome returned by AutoMan
	*							
	*/
	def launchCheckboxDistTask(taskID: String, task : Task) : Unit = {
		var ci : ConfidenceInterval = UnconstrainedCI()
		if (task.confidenceInt > 0) {
			ci = SymmetricCI(task.confidenceInt)
		}

	}
}
