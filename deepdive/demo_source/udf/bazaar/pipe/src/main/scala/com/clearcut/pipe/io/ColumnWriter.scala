package com.clearcut.pipe.io

import java.io.{File, OutputStreamWriter, FileOutputStream, BufferedWriter}
import com.clearcut.pipe.model._

import com.clearcut.pipe.Schema

class ColumnWriter(dir:String) extends Writer {
  val BUFFER_SIZE = 10 * 1024 * 1024

  var writers:Array[BufferedWriter] = null

  def setSchema(schema:Schema): Unit = {
    if (! new File(dir).exists)
      new File(dir).mkdirs()
    writers = schema.annTyps.map(t => {
      val name = dir + "/ann." + lowerFirst(t)
      if (new File(name).exists)
        null
      else
        new BufferedWriter(
          new OutputStreamWriter(new FileOutputStream(name)), BUFFER_SIZE)
    })
  }

  def write(annotations:Seq[AnyRef]) = {
    for (i <- 0 until writers.length) {
      if (writers(i) != null) {
        val json = Json.write(annotations(i))
        writers(i).write(json)
        writers(i).newLine()
      }
    }
  }

  def close =
    for (w <- writers)
      if (w != null) w.close()
}
