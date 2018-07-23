enablePlugins(PackPlugin)

name := "PyautomanlibPrototype"
version := "1.0"
scalaVersion := "2.11.7"
packMain := Map("PyAutoManRpcServer" -> "pyautomanlib.EstimationPrototypeServicer")

libraryDependencies ++= Seq(
    "io.grpc" % "grpc-netty" % scalapb.compiler.Version.grpcJavaVersion ,
    "com.thesamet.scalapb" %% "scalapb-runtime-grpc" % scalapb.compiler.Version.scalapbVersion ,
    "edu.umass.cs" %% "automan" % "1.2.0"
)

PB.targets in Compile := Seq(
  scalapb.gen() -> (sourceManaged in Compile).value
)


