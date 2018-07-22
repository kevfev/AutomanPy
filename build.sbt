name := "EstimationPrototype"

version := "1.0"

libraryDependencies ++= Seq(
    "io.grpc" % "grpc-netty" % scalapb.compiler.Version.grpcJavaVersion,
    "com.thesamet.scalapb" %% "scalapb-runtime-grpc" % scalapb.compiler.Version.scalapbVersion,
    "edu.umass.cs" %% "automan" % "1.2.0"
)

scalaVersion := "2.11.7"

assemblyOutputPath:= baseDirectory.value /"src/main/pyautomanlib/core/rpc"

PB.targets in Compile := Seq(
  scalapb.gen() -> (sourceManaged in Compile).value
)
