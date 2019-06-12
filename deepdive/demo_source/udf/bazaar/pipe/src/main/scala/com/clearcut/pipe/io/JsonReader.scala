package com.clearcut.pipe.io

import java.nio.charset.CodingErrorAction

import com.clearcut.pipe.Schema
import com.clearcut.pipe.model.{Id, Text}

import org.json4s._
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization

import scala.io.Source

class JsonReader(in:String,
                 idKey:String, documentKey:String)
  extends Reader with Iterator[Array[AnyRef]] {
  val BUFFER_SIZE = 10 * 1024 * 1024

  implicit val codec = new scala.io.Codec(
    java.nio.charset.Charset.forName("utf-8"))
  codec.onMalformedInput(CodingErrorAction.IGNORE)
  codec.onUnmappableCharacter(CodingErrorAction.IGNORE)

  val reader = Source.fromFile(new java.io.File(in), BUFFER_SIZE)

  var it = reader.getLines.zipWithIndex
  var _next = fetchNext()

  override def getSchema:Schema =
    Schema.createSchema("id", "text")

  override def hasNext: Boolean =
    _next != null

  override def next(): Array[AnyRef] = {
    val n = _next
    _next = fetchNext()
    n
  }

  private def fetchNext(): Array[AnyRef] = {
    var n:Array[AnyRef] = null
    while (n == null && it.hasNext) {
      val (line, num) = it.next

      val json = parse(line)

      implicit val formats = DefaultFormats

      try {
        val documentId = (json \ idKey).extract[String]
        val documentStr = (json \ documentKey).extract[String]

        n = Array(documentId, documentStr)

      } catch {
        case e:Exception =>
          System.err.println(s"Warning: skipped malformed line ${num}: ${line}")
      }
    }
    n
  }

  def close =
    reader.close
}
