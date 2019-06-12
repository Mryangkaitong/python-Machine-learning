package com.clearcut.nlp

import play.api.libs.json.{JsObject, JsString, JsValue, Json}

import scala.io.Source

class JSONReader(input:Source, docIdKeys:Array[String], documentKey:String)
  extends Iterator[(Array[String], String)] {

  var it = input.getLines.zipWithIndex
  var _next = fetchNext()

  override def hasNext: Boolean =
    _next != null

  override def next(): (Array[String], String) = {
    val n = _next
    _next = fetchNext()
    n
  }

  private def fetchNext(): (Array[String], String) = {
    var n:(Array[String], String) = null
    while (n == null && it.hasNext) {
      val (line, num) = it.next

      val jsObj = Json.parse(line).asInstanceOf[JsObject]

      val maybeDocumentIds = new Array[String](docIdKeys.length)
      docIdKeys.zipWithIndex.foreach { case (idk, i) =>
        val maybeDocumentId = jsObj.value.get(idk);
        (maybeDocumentId) match {
          case (Some(documentId:JsString)) =>
            maybeDocumentIds(i) = documentId.value
          case (_) =>
            maybeDocumentIds(i) = "\\N"
        }
      }

      val maybeDocumentStr = jsObj.value.get(documentKey).map(_.asInstanceOf[JsString].value)

      (maybeDocumentIds, maybeDocumentStr) match {
        case (documentIds:Array[String], Some(documentStr:String)) =>
          n = (documentIds, documentStr)
        //case (Array[None],_) =>
        //  System.err.println(s"Warning: skipped malformed line ${num}: ${line}")
        case (_, None) =>
          System.err.println(s"Warning: skipped malformed line ${num}: ${line}")
      }
    }
    n
  }
}
