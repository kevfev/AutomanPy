package pyautomanlib;
import edu.umass.cs.automan.core.answer._;
import automanlib_rpc._;
import automanlib_rpc.AutomanTask.TaskType;
import automanlib_rpc.AutomanOutcome;
import automanlib_classes._;
import automanlib_wrappers._;
import scala.concurrent.{ ExecutionContext, Future };
import java.util.concurrent.{Executors, ExecutorService, ConcurrentLinkedQueue, ConcurrentHashMap, ConcurrentMap}
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.{AbstractQueue, UUID};

object PyautomanPrototypeServicer extends GrpcServer{ self => 
	Thread.currentThread().setName("RPC-AutoMan-Server");
	private class PyautomanServicer extends PyautomanPrototypeGrpc.PyautomanPrototype {	
		val taskQueue: AbstractQueue[(String, AutomanTask.TaskType)] = new ConcurrentLinkedQueue;
		val answerMap: ConcurrentMap[String, AnyRef] = new ConcurrentHashMap;
		val workerPool: ExecutorService = Executors.newSingleThreadExecutor();
		var stopWorkers: AtomicBoolean = new AtomicBoolean(false);
		val pollFrequency: Int = 6000;


		Thread.currentThread().setName("RPC-AutoMan-Server-Thread");

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

		/** waits on the result specified by ID. This method calculates the max number of checks (plus a few extra) to make
		*	based on the specified question timeout for the task. For example, if the user made a task with a question timeout
		*	multiplier of 5 (minutes), and our pollFrequency is 6000 (6 seconds), then we should perform a max of 
		*	(5*60*1000/6000) + 10 = 60 checks. If we don't see a response, we need to send back an error (worker probably crashed)
		*
		*  @param task - submitted task
		*  @return the Future outcome returned by AutoMan for this task ID
		*							
		*/
		def waitOnResult(id: String, timeout_seconds: Int) : AnyRef = {
			var wait_count : Int = 0;
			val max_checks = (timeout_seconds * pollFrequency/1000) + 10;
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
			val automan_outcome = waitOnResult(taskId, timeout)
			val outcome = task.taskType match{
				case TaskType.Estimate(etask)		=> 	makeEstimateOutcome(automan_outcome.asInstanceOf[EstimationOutcome]);
				case TaskType.Multiestimate(metask) => 	makeMultiEstimateOutcome(automan_outcome.asInstanceOf[MultiEstimationOutcome]);
				case TaskType.Freetext(frtask)		=>	makeFreetextOutcome(automan_outcome.asInstanceOf[ScalarOutcome[Symbol]]);
				case TaskType.FreetextDist(frdtask) =>	makeFreetextDistOutcome(automan_outcome.asInstanceOf[VectorOutcome[Symbol]]);
				case TaskType.Radio(rtask) 			=>	makeRadioOutcome(automan_outcome.asInstanceOf[ScalarOutcome[Symbol]]);
				case TaskType.RadioDist(rdtask) 	=>	makeRadioDistOutcome(automan_outcome.asInstanceOf[VectorOutcome[Symbol]]);
				case TaskType.Checkbox(chtask) 		=>	makeCheckboxOutcome(automan_outcome.asInstanceOf[ScalarOutcome[Symbol]]);
				case TaskType.CheckboxDist(chdtask) =>	makeCheckboxDistOutcome(automan_outcome.asInstanceOf[VectorOutcome[Symbol]]);
				case TaskType.Empty					=>	println("ERROR: Unknown type of task received by RPC AutoMan worker. Server generated bad task");
														AutomanOutcome().withEmptyOutcome(Empty());
			}
			return TaskResponse().withReturnCode(TaskResponse.TaskReturnCode.VALID).withOutcome(outcome);
		}

		/**  make an EstimateOutcome message with answer field set
		*
		*  @param automan_outcome - the outcome returned by automan, cast to it's correct type
		*  @return an EstimateOutcome with all fields initialized
		*							
		*/
		def makeEstimateOutcome(automan_outcome: EstimationOutcome): AutomanOutcome = {
			var _est : Double=0.0;
			var _low : Double=0.0;
			var _high: Double=0.0;
			var _cost: Double=0.0;
			var _conf: Double=0.0;
			var _need : Double=0.0;
			var _have : Double=0.0;
			var outcome_type: OutcomeType = OutcomeType.UNKNOWN_OUTCOME
			automan_outcome.answer match{
				case Estimate(est, low, high, cost, conf, _, _) => 	_est =est.toDouble;
																	_low =low.toDouble;
																	_high =high.toDouble;
																	_cost =cost.toDouble;
																	_conf =conf.toDouble;
																	outcome_type = OutcomeType.CONFIDENT;
				case LowConfidenceEstimate(est, low, high, cost, conf, _, _) => _est =est.toDouble;
																				_low =low.toDouble;
																				_high =high.toDouble;
																				_cost =cost.toDouble;
																				_conf =conf.toDouble;
																				outcome_type = OutcomeType.LOW_CONFIDENCE
				case OverBudgetEstimate(need, have, _) =>	_need =need.toDouble;
															_have =have.toDouble;
															outcome_type= OutcomeType.OVERBUDGET
			}
			if((outcome_type == OutcomeType.CONFIDENT)||(outcome_type == OutcomeType.LOW_CONFIDENCE)){
				return AutomanOutcome().withEstimateOutcome(EstimateOutcome().withAnswer(ValueOutcome(est = _est,low = _low,high = _high,cost = _cost,conf = _conf))
															.withNeed(-1.0)
															.withHave(-1.0)
															.withOutcomeType(outcome_type));
			}
			return AutomanOutcome().withEstimateOutcome(EstimateOutcome().withOutcomeType(OutcomeType.OVERBUDGET)
														.withNeed(_need)
														.withHave(_have));
		}

		/**  make a MultiEstimateOutcome message with answer field set
		*
		*  @param automan_outcome - the outcome returned by automan, cast to it's correct type
		*  @return a MultiEstimateOutcome with all fields initialized
		*							
		*/
		def makeMultiEstimateOutcome(automan_outcome: MultiEstimationOutcome): AutomanOutcome = {
			//TODO
			return AutomanOutcome()
		}

		/**  make a RadioOutcome message with answer field set
		*
		*  @param automan_outcome - the outcome returned by automan, cast to it's correct type
		*  @return a RadioOutcome with all fields initialized
		*							
		*/
		def makeRadioOutcome(automan_outcome: ScalarOutcome[Symbol]): AutomanOutcome = {
			var _option: String = "n/a" ;
			var _cost: Double=0.0;
			var _conf: Double=0.0;
			var _need : Double=0.0;
			var _have : Double=0.0;
			var outcome_type: OutcomeType = OutcomeType.CONFIDENT;
			automan_outcome.answer match{
				case Answer(value, cost, conf, _, _) => _option = value.asInstanceOf[Symbol].toString;
														_cost =cost.toDouble;
														_conf =conf.toDouble;
														outcome_type  = OutcomeType.CONFIDENT;
				case LowConfidenceAnswer(value, cost, conf, _, _) => _option = value.asInstanceOf[Symbol].toString;
																	_cost =cost.toDouble;
																	_conf =conf.toDouble;
																	outcome_type = OutcomeType.LOW_CONFIDENCE
				case OverBudgetAnswer(need, have, _) =>	_need =need.toDouble;
														_have =have.toDouble;
														outcome_type = OutcomeType.OVERBUDGET
			}
		 	if((outcome_type == OutcomeType.CONFIDENT) || (outcome_type == OutcomeType.LOW_CONFIDENCE)){
				return AutomanOutcome().withRadioOutcome(RadioOutcome().withAnswer(StringOutcome(option=_option, cost=_cost, conf=_conf))
														.withNeed(-1.0)
														.withHave(-1.0)
														.withOutcomeType(outcome_type));
			}
			return AutomanOutcome().withRadioOutcome(RadioOutcome().withOutcomeType(OutcomeType.OVERBUDGET)
													.withNeed(_need.toDouble)
													.withHave(_have.toDouble));
		}

		/**  make a RadioDistOutcome message with answer field set
		*
		*  @param automan_outcome - the outcome returned by automan, cast to it's correct type
		*  @return a RadioDistOutcome with all fields initialized
		*							
		*/
		def makeRadioDistOutcome(automan_outcome: VectorOutcome[Symbol]): AutomanOutcome = {
			//TODO
			return AutomanOutcome()
		}

		/**  make a FreetextOutcome message with answer field set
		*
		*  @param automan_outcome - the outcome returned by automan, cast to it's correct type
		*  @return a FreetextOutcome with all fields initialized
		*							
		*/
		def makeFreetextOutcome(automan_outcome: ScalarOutcome[Symbol]): AutomanOutcome = {
			//TODO
			return AutomanOutcome();
		}

		/**  make a FreetextDistOutcome message with answer field set
		*
		*  @param automan_outcome - the outcome returned by automan, cast to it's correct type
		*  @return a FreetextDistOutcome with all fields initialized
		*							
		*/
		def makeFreetextDistOutcome(automan_outcome: VectorOutcome[Symbol]): AutomanOutcome = {
			//TODO
			return AutomanOutcome()
		}

		/**  make a CheckboxOutcome message with answer field set
		*
		*  @param automan_outcome - the outcome returned by automan, cast to it's correct type
		*  @return a CheckboxOutcome with all fields initialized
		*							
		*/
		def makeCheckboxOutcome(automan_outcome: ScalarOutcome[Symbol]): AutomanOutcome = {
			//TODO
			return AutomanOutcome()
		}

		/**  make a CheckboxDistOutcome message with answer field set
		*
		*  @param automan_outcome - the outcome returned by automan, cast to it's correct type
		*  @return a CheckboxDistOutcome with all fields initialized
		*							
		*/
		def makeCheckboxDistOutcome(automan_outcome: VectorOutcome[Symbol]): AutomanOutcome = {
			//TODO
			return AutomanOutcome()
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