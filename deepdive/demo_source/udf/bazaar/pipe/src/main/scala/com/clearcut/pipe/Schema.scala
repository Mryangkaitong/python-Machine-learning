package com.clearcut.pipe

import com.clearcut.pipe.annotator.Annotator
import scala.collection.mutable.Map

case class Schema
(
  annTyps: Array[String] = Array(),
  defaults: Map[String, Int] = Map(),
  provenance: Array[String] = Array()
)


object Schema {

  def defaultAnnotations(schema: Schema, needed: Seq[String], all: Seq[String]): Seq[AnyRef] = {
    defaultAnnotationIndices(schema, needed).map(all(_))
  }

  def defaultAnnotationIndices(schema: Schema, needed: Seq[String]): Seq[Int] = {
    needed.map(schema.defaults(_))
  }

  def extendSchema(before: Schema, annotators: Array[Annotator[_,_]]): Schema = {
    val annTyps = Array.concat(before.annTyps, annotators.flatMap(_.generates))
    val defaults = Map[String, Int]()
    defaults ++= before.defaults
    annTyps.zipWithIndex.foreach { case (c, i) => if (!defaults.contains(c)) defaults += (c -> i) }
    val provenance = Array.concat(before.provenance, annotators.flatMap(_.generates))
    new Schema(annTyps, defaults, provenance)
  }

  def createSchema(annTyps: String*): Schema = {
    val defaults = Map[String, Int]()
    annTyps.zipWithIndex.foreach { case (c, i) => if (!defaults.contains(c)) defaults += (c -> i) }
    val provenance = annTyps.toArray.map(_ => "provided")
    new Schema(annTyps.toArray, defaults, provenance)
  }

  def prettyPrint(s:Schema) = {
    s.annTyps.map(println(_))
  }

}