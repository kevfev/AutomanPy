package pyautomanlib;
import edu.umass.cs.automan.core.answer._;
import automanlib_rpc._;
import automanlib_rpc.AutomanTask.TaskType;
import automanlib_classes._;
import automanlib_wrappers._;
import scala.concurrent.{ ExecutionContext, Future };
import java.util.concurrent.{Executors, ExecutorService, ConcurrentLinkedQueue, ConcurrentHashMap, ConcurrentMap}
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.{AbstractQueue, UUID};

object PyautomanPrototypeServicer extends GrpcServer{ self => 
	private class PyautomanServicer extends PyautomanPrototypeGrpc.PyautomanPrototype {	
		val taskQueue: AbstractQueue[(String, AutomanTask.TaskType)] = new ConcurrentLinkedQueue;
		val answerMap: ConcurrentMap[String, AnyRef] = new ConcurrentHashMap;
		val workerPool: ExecutorService = Executors.newSingleThreadExecutor();
		var stopWorkers: AtomicBoolean = new AtomicBoolean(false);
		val pollFrequency: Int = 6000;

		/** rpc method used by client to submit a task to Automan.
		*
		*  @param automanTask - submitted task
		*  @return a new future TaskRespone instance with the outcome of the task. Check for any errors
		*				set in "return_code" field. If field is valid then outcome is valid, else
		*				an error occured
		*							
		*/
		def submitTask(automanTask: AutomanTask) : Future[TaskResponse] = {
			val task_id : String = java.util.UUID.randomUUID.toString;
			val response = executeTask(taskId = task_id, task=automanTask);
			Future.successful(response);
		}

		/**  make and EstimateOutcome with ValueOutcome message field set
		*
		*  @param _est - estimate returned by AutoMan
		*  @param _low - lowest worker response
		*  @param _high - highest worker response
		*  @param _cost - cost of task
		*  @param _conf - confidence of result
		*  @return an EstimateOutcome with all fields but outcomeType initialized
		*							
		*/
		def makeValueOutcome( _est : BigDecimal, _low : BigDecimal, _high: BigDecimal, _cost: BigDecimal, _conf: BigDecimal, outcome_type: OutcomeType): EstimateOutcome = {
			return EstimateOutcome().withAnswer(ValueOutcome(est = _est.toDouble,low = _low.toDouble,high = _high.toDouble,cost = _cost.toDouble,conf = _conf.toDouble))
									.withNeed(-1.0)
									.withHave(-1.0)
									.withOutcomeType(outcome_type);
		}

		/** make an overbudget EstimateOutcome
		*
		*  @param _need - the amount needed by AutoMan to continue trying the task
		*  @param _have - the amount originally allocated for the task
		*  @return an EstimateOutcome for an overbudget result
		*							
		*/
		def makeOverBudgetOutcome( _need: BigDecimal, _have: BigDecimal): EstimateOutcome = {
			return EstimateOutcome().withOutcomeType(OutcomeType.OVERBUDGET)
									.withNeed(_need.toDouble)
									.withHave(_have.toDouble);
		}


		/** waits on the result specified by ID. This method calculates the max number of checks (plus a few extra) to make
		*	based on the specified question timeout for the task. For example, if the user made a task with a question timeout
		*	multiplier of 5 (minutes), and our pollFrequency is 6000 (6 seconds), then we should perform a max of 
		*	(5*60*1000/6000) + 10 = 60 checks. If we don't see a response, we need to send back an error (worker probably crashed)
		*
		*  @param task - submitted task
		*  @return the Future outcome returned by AutoMan for this task ID
		*							
		*/
		def waitOnResult(id: String, timeout_minutes: Int) : AnyRef = {
			var wait_count : Int = 0;
			val max_checks = (timeout_minutes * 60.0 * 1000.0 / pollFrequency) + 10.0;
			while(answerMap.get(id) == null)
			{
				Thread.sleep(pollFrequency);
				wait_count = wait_count + 1;
				if (wait_count > max_checks){
					println("ERROR: Server timed out waiting for response to task. Worker Thread may have crashed. Server terminating.. ");
					System.exit(1);
				}
			}
			
			return answerMap.remove(id);
		}

		/** submits an estimate task to Automan worker
		*
		*  @param task - submitted task
		*  @return a new TaskResponse representing the outcome of the task. 
		*							
		*/
		def executeTask(taskId: String, task : AutomanTask) : TaskResponse = {	
			val timeout = task.timeout;
			taskQueue.add((taskId, task.taskType))
			val automan_outcome = waitOnResult(taskId, timeout).asInstanceOf[EstimationOutcome]
			val est_out = automan_outcome.answer match{
				case Estimate(est, low, high, cost, conf, _, _) => makeValueOutcome(est, low, high, cost, conf, OutcomeType.CONFIDENT);
				case LowConfidenceEstimate(est, low, high, cost, conf, _, _) => makeValueOutcome(est, low, high, cost, conf, OutcomeType.LOW_CONFIDENCE);
				case OverBudgetEstimate(need, have, _) => makeOverBudgetOutcome(need,have); 
			}
			return TaskResponse().withReturnCode(TaskResponse.TaskReturnCode.VALID).withEstimateOutcome(est_out);
		}

		

		/** rpc method used by client to register an adapter with one of the worker threads.
		*
		*  @param automanTask - submitted AdapterCredentials
		*  @return a new ServerStatusResponse indicating whether the credentials were added successfully or not
		*							
		*/
		def registerAdapter(adapter: AdapterCredentials) : Future[ServerStatusResponse] = {
			// add error checking for execute
			workerPool.execute(new AutomanWorker(worker_id= "wrkr-1", adptr= adapter,stopWorker= stopWorkers,
												 workQueue= taskQueue, resultMap= answerMap));
			var ssr: ServerStatusResponse = ServerStatusResponse().withReturnCode(ServerStatusResponse.StatReturnCode.SUCCESS)
			Future.successful(ssr);
		}

		/** Report the status of the server
		*
		*  @return a new ServerStatusResponse, representing the state of the server. Either Running or Killed
		*							
		*/
		def serverStatus(e: Empty) : Future[ServerStatusResponse] = {
			var ssr = ServerStatusResponse();
			if (self.running()){
				ssr.withReturnCode(ServerStatusResponse.StatReturnCode.RUNNING)
			}else{
				ssr.withReturnCode(ServerStatusResponse.StatReturnCode.KILLED)
			}
			Future.successful(ssr);
		}

		/** Shutdown the gRPC server
		*
		*  @return a new ServerStatusResponse, representing the state of the server. Either Running or Killed
		*							
		*/
		def killServer(e: Empty) : Future[ServerStatusResponse] = {
			println("Server Shutting Down..")
			stopWorkers.set(true);
			workerPool.shutdown();
			self.stop_server();
			Future.successful(ServerStatusResponse().withReturnCode(ServerStatusResponse.StatReturnCode.KILLED));
		}

	}

	def main(args: Array[String]) : Unit = {
		// add argument parsing
		var localport = 50051;
		var poolSize = 1;
		if(args.length >= 1) localport = args(0).toInt;
		if(args.length >= 2) poolSize = args(1).toInt;
		val ssdef = PyautomanPrototypeGrpc.bindService(new PyautomanServicer(), ExecutionContext.global);
		println("Server Started on port "+localport+" ...");
		println("Worker poolsize: "+poolSize);
		runServer(ssd = ssdef, port = localport);
	}
}