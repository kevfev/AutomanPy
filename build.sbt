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

excludeDependencies ++= Seq(
  ExclusionRule("commons-logging", "commons-logging"),
  ExclusionRule("xml-apis", "xml-apis"),
  ExclusionRule("commons-collections", "commons-collections"),
  ExclusionRule("commons-discovery", "commons-discovery"),
  ExclusionRule("commons-logging", "commons-discovery"),
  ExclusionRule("commons-lang", "commons-lang"),
  ExclusionRule("dom4j", "dom4j"),
  ExclusionRule("commons-pool", "commons-pool"),
  ExclusionRule("commons-digester", "commons-digester"),
  ExclusionRule("commons-codec", "commons-codec")
)

PB.targets in Compile := Seq(
  scalapb.gen() -> (sourceManaged in Compile).value
)


