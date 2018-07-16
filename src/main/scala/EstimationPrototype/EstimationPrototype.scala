package automanlib;
import edu.umass.cs.automan.adapters.mturk.DSL._
import automanlib_rpc._;
import automanlib_classes._;
import scala.concurrent.{ ExecutionContext, Future };


object EstimationPrototypeServicer extends GrpcServer{ self => 
	private class EstimationServicer extends EstimationPrototypeGrpc.EstimationPrototype {
		private var _adptr_credentials: Option[AdapterCredentials] = None;
		
		/** rpc function used by client to submit a task to Automan
		*
		*  @param task_request - submitted task
		*  @return a new TaskRespone instance with the outcome of the task. Check for any errors
		*				set in "return_code" field. If field is valid then outcome is valid, else
		*				an error occured
		*							
		*/
		def submitTask(task_request: AutomanTask) : Future[TaskResponse] = {
			var response: TaskResponse = TaskResponse()
			println("Received Task")
			task_request.request match {
				case Some(req)  => 
					_adptr_credentials match {
						case Some(adptr) => 
							var o = estimateTask(req, adptr); 
							response = response.withReturnCode(TaskResponse.TaskReturnCode.VALID)
									.withOutcome(o);
						case _ => 
							response =response.withReturnCode(TaskResponse.TaskReturnCode.ERROR)
									.withErrMsg("ERROR: no credentials registered"); 
							println("ERROR: no credentials registered");
					}
				case _ => 
							response =response.withReturnCode(TaskResponse.TaskReturnCode.ERROR)
									.withErrCode(TaskResponse.ErrorCode.NO_CREDENTIALS_REGISTERED)
									.withErrMsg("ERROR: Invalid task"); 
							println("ERROR: Invalid task");
			}
			val tr: TaskResponse = response
			Future.successful(tr);
		}

		/** internal function used by server, submits a estimate task to Automan
		*
		*  @param task - submitted task
		*  @param adptr - adapter with credentials to connect to the crowdsource back-end
		*  @return a new TaskOutcome, representing the outcome of the task. 
		*							
		*/
		def estimateTask(task : Task, adptr: AdapterCredentials) : TaskOutcome = {

			def make_est_reply( _est : BigDecimal, _low : BigDecimal, _high: BigDecimal, _cost: BigDecimal, _conf: BigDecimal, outcome_type : TaskOutcome.OutcomeType): TaskOutcome = {
				val e: OutcomeAnswer = OutcomeAnswer().withEstimateAnswer(EstimateOutcome(est = _est.toDouble,low = _low.toDouble,high = _high.toDouble,cost = _cost.toDouble,conf = _conf.toDouble));
				val o: TaskOutcome = TaskOutcome().withAnswer(List(e)).withOutcomeType(outcome_type);
				return o;
			}


			def make_overbudg_est( _need: BigDecimal, _have: BigDecimal): TaskOutcome = {
				val e: OutcomeAnswer = OutcomeAnswer().withOverBudgetAnswer(OverBudgetOutcome(need = _need.toDouble, have = _have.toDouble));
				val o: TaskOutcome = TaskOutcome().withAnswer(List(e)).withOutcomeType(TaskOutcome.OutcomeType.OVER_BUDGET_EST);
				return o;
			}

			implicit val mt = mturk (
			   access_key_id = adptr.accessId,
			   secret_access_key = adptr.accessKey,
			   sandbox_mode = adptr.adapterOptions("sandbox_mode").toBoolean
			)
						
			def est(title_ : String ,text_ : String, budget_ : Double, image_url_ : String) = estimate(
				default_sample_size = 2,
				text = text_ ,
				title = title_ ,
				image_url = image_url_ ,
				budget = budget_ ,
				question_timeout_multiplier = 3
			)
			
			automan(mt) {
				// ask humans for answers
				val outcome = est(title_ = task.title, text_ =task.text, budget_ =task.budget, image_url_ =task.imgUrl);
				var ans = TaskOutcome()
				outcome.answer match{
					case Estimate(est, low, high, cost, conf, _, _) => 
						println("estimated,"); 
						ans = make_est_reply(est, low, high, cost, conf, TaskOutcome.OutcomeType.ESTIMATE);
					case LowConfidenceEstimate(est, low, high, cost, conf, _, _) => 
						println("low conf estimated,");
						ans = make_est_reply(est, low, high, cost, conf, TaskOutcome.OutcomeType.LOW_CONFIDENCE_EST);
					case OverBudgetEstimate(need, have, _) => 
						println("overbudget,");
						ans = make_overbudg_est(need,have);
				}
				return ans
			}
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

		/** Register a crowdsource back-end adapter to the server.
		*
		*  @param adptr - adapter with credentials to connect to the crowdsource back-end
		*  @return a new RegistrationResponse, representing the whether the adapter was registered successfully or not
		*							
		*/
		def registerAdapter(adptr : AdapterCredentials) : Future[RegistrationResponse] = {
			// add error checking
			_adptr_credentials = Some(adptr);
			Future.successful(RegistrationResponse().withReturnCode(RegistrationResponse.RegReturnCode.OKAY));
		}

		/** Shutdown the gRPC server
		*
		*  @return a new ServerStatusResponse, representing the state of the server. Either Running or Killed
		*							
		*/
		def killServer(e: Empty) : Future[ServerStatusResponse] = {
			println("Server Shutting Down..")
			self.stop_server();
			Future.successful(ServerStatusResponse().withReturnCode(ServerStatusResponse.StatReturnCode.KILLED));
		}

	}

	def main(args: Array[String]) : Unit = {
		// add argument parsing
		var localport = 50051;
		if(args.length >1) localport = args(0).toInt;

		val ssdef = EstimationPrototypeGrpc.bindService(new EstimationServicer(), ExecutionContext.global)
		println("Server Started on port "+localport+" ...")
		runServer(ssd = ssdef, port = localport)
	}
}