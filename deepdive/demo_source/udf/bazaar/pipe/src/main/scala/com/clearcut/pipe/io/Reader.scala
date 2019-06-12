package com.clearcut.pipe.io

import com.clearcut.pipe.Schema

trait Reader extends Iterator[Array[AnyRef]] {
  def getSchema:Schema
  def close
}
