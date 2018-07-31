/*
 * Copyright 2017 Petra Bierleutgeb
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package pyautomanlib;

import io.grpc.{ Server, ServerBuilder, ServerServiceDefinition }

trait GrpcServer {
	private[this] var server :Server = null;
  private[this] var status :Int = 0;
  private[this] var running_status: Boolean = false;
  private[this] val poolSize: Int = 1;

  def start_server(): Unit = {
    server.start()
    running_status = true;
  }

  def running(): Boolean = {
    if(running_status) return true;
    return false;
  }
  def stop_server(): Unit ={
    running_status = false;
  	server.shutdown()
  }
  def runServer(ssd: ServerServiceDefinition, port: Int): Unit = {
    server = ServerBuilder
      .forPort(port)
      .addService(ssd)
      .build
      .start

    // make sure our server is stopped when jvm is shut down
    Runtime.getRuntime.addShutdownHook(new Thread() {
      override def run(): Unit = server.shutdown()
    })

    server.awaitTermination()
  }

}