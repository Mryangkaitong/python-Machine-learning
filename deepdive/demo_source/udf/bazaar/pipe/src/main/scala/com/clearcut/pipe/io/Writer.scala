package com.clearcut.pipe.io

import com.clearcut.pipe.Schema

trait Writer {
  def setSchema(s:Schema)
  def write(annotations:Seq[AnyRef])
  def close
}
