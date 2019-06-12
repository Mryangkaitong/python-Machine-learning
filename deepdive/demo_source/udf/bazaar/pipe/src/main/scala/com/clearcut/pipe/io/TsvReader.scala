package com.clearcut.pipe.io

import java.nio.charset.CodingErrorAction

import com.clearcut.pipe.Schema
import com.clearcut.pipe.model.{Text, Id}

import scala.io.{Source, BufferedSource}

class TsvReader(in:String = null,
                idCol:Int = 0, documentCol:Int = 1,
                inSource:Source = null)
  extends Reader with Iterator[Array[AnyRef]] {

  implicit val codec = new scala.io.Codec(
    java.nio.charset.Charset.forName("utf-8"))
  codec.onMalformedInput(CodingErrorAction.IGNORE)
  codec.onUnmappableCharacter(CodingErrorAction.IGNORE)

  val reader = if (inSource != null) inSource else Source.fromFile(in)

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

  // should unescape \, \r, \n, \t
  private def fetchNext(): Array[AnyRef] = {
    var n:Array[AnyRef] = null
    while (n == null && it.hasNext) {
      val (line, num) = it.next
      val tsvArr = line.trim.split("\t")
      if (tsvArr.length >= 2) {
        val documentId = tsvArr(idCol)
        val documentStr = unescape(tsvArr(documentCol))
        n = Array(documentId, documentStr)
      } else {
        System.err.println(s"Warning: skipped malformed line ${num}: ${line}")
      }
    }
    n
  }

  private def unescape(s:String):String = {
    val sb = new StringBuilder()
    val NORMAL = 0
    val ESCAPE = 1

    var state = NORMAL

    for (i <- 0 until s.length) {
      val c = s.charAt(i)
      //val l = if (i == s.length - 1) Character.UNASSIGNED else s.charAt(i+1)
      state match {
        case NORMAL =>
          c match {
            case '\\' => state = ESCAPE
            case _ => sb.append(c)
          }
        case ESCAPE =>
          c match {
            case 'r' => sb.append('\r'); state = NORMAL
            case 'n' => sb.append('\n'); state = NORMAL
            case 't' => sb.append('\t'); state = NORMAL
            case '\\' => sb.append('\\'); state = NORMAL
            case _ =>
              println("ERROR")
          }
      }
    }
    return sb.toString
  }

  def close =
    reader.close
}