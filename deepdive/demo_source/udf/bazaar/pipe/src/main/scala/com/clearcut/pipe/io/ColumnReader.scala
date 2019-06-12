package com.clearcut.pipe.io

import java.io._
import com.clearcut.pipe.Schema
import com.clearcut.pipe.model._

class ColumnReader(dir:String) extends Reader with Iterator[Array[AnyRef]] {

  val schema = Schema.createSchema(
    // The schema is determined based on file name suffixes
    new File(dir).list.map(n => n.substring(n.lastIndexOf(".") + 1)).map(lowerFirst(_)):_*
  )

  val readers = new File(dir).listFiles.map(f => new BufferedReader
    (new InputStreamReader(new FileInputStream(f))))

  var _next = fetchNext()

  def getSchema(): Schema = schema

  override def hasNext: Boolean =
    _next != null

  override def next():Array[AnyRef] = {
    val n = _next
    _next = fetchNext()
    n
  }

  private def fetchNext(): Array[AnyRef] = {
    readers.zip(schema.annTyps).map { case (r,t) => {
      val line = r.readLine
      if (line == null)
        return null

      Json.read[AnyRef](line, Util.name2clazz(t))
    }}
  }

  def close = {
    readers.map(_.close)
  }
}
