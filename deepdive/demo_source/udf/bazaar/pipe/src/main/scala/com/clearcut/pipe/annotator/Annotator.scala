package com.clearcut.pipe.annotator

import java.util.Properties
import scala.reflect.runtime.universe._
import com.clearcut.pipe.model._

abstract class Annotator[In,Out](implicit inTag:TypeTag[In], outTag:TypeTag[Out])
  extends java.io.Serializable {

  var properties = new Properties()

  def setProperties(p:java.util.Properties) = {
    properties = p
  }

  def annotate(in:In):Out

  def init = {}

  def close = {}

  def requires = inTypes

  def generates = outTypes

  val inTypes:Seq[String] = toTypes(inTag)
  val outTypes:Seq[String] = toTypes(outTag)

  private def toTypes[A](tag:TypeTag[A]):Seq[String] = {
    if (tag.tpe <:< typeOf[Product])
      tag.tpe.typeArgs.map(t => {
        val s = t.toString
        lowerFirst(s.substring(s.lastIndexOf(".") + 1))
      }) else {
      val s = tag.tpe.toString
      Array(lowerFirst(s.substring(s.lastIndexOf(".") + 1)))
    }
  }

  val inClazz = inTag.mirror.runtimeClass(inTag.tpe.typeSymbol.asClass)

  def annotateUnsafe(in:AnyRef*):Seq[AnyRef] = {
    var outTuple:Out = if (inTypes.size == 1) {
      val inTuple = in(0).asInstanceOf[In]
      annotate(inTuple)
    } else {
      val inTuple = inClazz.getConstructors.apply(0).newInstance(in:_*).asInstanceOf[In]
      annotate(inTuple)
    }
    var outSeq = if (outTypes.size == 1)
      Seq(outTuple.asInstanceOf[AnyRef])
    else
      outTuple.asInstanceOf[Product].productIterator.toSeq.asInstanceOf[Seq[AnyRef]]
    outSeq
  }
}
