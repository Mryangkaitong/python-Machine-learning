package com.clearcut.pipe.io

import org.json4s.Extraction._
import org.json4s.NoTypeHints
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization
import org.json4s.reflect.Reflector

object Json {

  implicit val formats = Serialization.formats(NoTypeHints)

  def write[A <: AnyRef](o:A)(implicit m:Manifest[A]):String =
    Serialization.write[A](o)

  def read[AnyRef](s:String, t:Class[_]):AnyRef = {
    val json = parse(s)
    extract(json, Reflector.scalaTypeOf(t)).asInstanceOf[AnyRef]
  }

  def read[A](s:String)(implicit m:Manifest[A]):A =
    Serialization.read[A](s)
}
