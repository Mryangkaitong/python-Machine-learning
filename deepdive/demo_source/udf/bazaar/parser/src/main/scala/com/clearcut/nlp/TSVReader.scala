package com.clearcut.nlp

import scala.io.BufferedSource

class TSVReader(input:BufferedSource,
                 idCols:Array[Int], documentCol:Int)
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
      val tsvArr = line.trim.split("\t")
      if (tsvArr.length >= idCols.length + 1) {
        val documentIds = idCols.map(idc => tsvArr(idc))
        val documentStr = tsvArr(documentCol)
        n = (documentIds, documentStr)
      } else {
        System.err.println(s"Warning: skipped malformed line ${num}: ${line}")
      }
    }
    n
  }
}
