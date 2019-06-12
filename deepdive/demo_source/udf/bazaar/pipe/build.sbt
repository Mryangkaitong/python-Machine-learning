import com.typesafe.sbt.SbtStartScript

organization := "com.clearcut"

name := "pipe"

version := "0.1-SNAPSHOT"

scalaVersion := "2.11.7"

resolvers += "Typesafe Repository" at "http://repo.typesafe.com/typesafe/releases/"

resolvers += "Scalaz Bintray Repo" at "https://dl.bintray.com/scalaz/releases"

libraryDependencies ++= List(
  "ch.qos.logback" % "logback-classic" % "1.0.7",
  "com.typesafe.play" %% "play-json" % "2.3.4",
  "com.github.scopt" %% "scopt" % "3.2.0",
  "edu.stanford.nlp" % "stanford-corenlp" % "3.6.0",
  "edu.stanford.nlp" % "stanford-corenlp" % "3.6.0" classifier "models",
  "org.scalatest" % "scalatest_2.11" % "2.2.5" % "test",
  "org.http4s" %% "http4s-dsl" % "0.7.0",
  "org.http4s" %% "http4s-jetty" % "0.7.0",
  "org.json4s" %% "json4s-jackson" % "3.2.11",
  "org.jsoup" % "jsoup" % "1.8.3"
)

unmanagedJars in Compile += file("lib/stanford-srparser-2014-10-23-models.jar")

parallelExecution in Test := false

test in assembly := {}

seq(SbtStartScript.startScriptForClassesSettings: _*)

