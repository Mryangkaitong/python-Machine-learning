package com.clearcut.pipe.io

import java.io.{FileOutputStream, OutputStreamWriter, BufferedWriter}

import com.clearcut.pipe.Schema
import com.clearcut.pipe.model._

/** Legacy writer for psql readable TSV table.
 *
 * Example output:
 * 12	1	This is a simple example.	{"This","is","a","simple","example","."}
 *   {"this","be","a","simple","example","."}	{"DT","VBZ","DT","JJ","NN","."}
 *   {"O","O","O","O","O","O"}	{0,5,8,10,17,24}
 *   {"nsubj","cop","det","amod","",""}	{5,5,5,5,0,0}
 */
class TsvWriter(out:String = null, outWriter:BufferedWriter = null) extends Writer {

  val writer = if (outWriter != null) outWriter else
    new BufferedWriter(new OutputStreamWriter(new FileOutputStream(out), "utf-8"))

  var indices:Seq[Int] = null

  def setSchema(schema:Schema) = {
    indices = Schema.defaultAnnotationIndices(schema, Seq("Id", "Text", "SentenceOffsets",
      "SentenceTokenOffsets", "Tokens", "TokenOffsets", "Lemmas", "Poss",
      "NerTags", "SentenceDependencies"))
  }

  def write(annotations:Seq[AnyRef]) = {
    val is = indices.map(annotations(_))
    val id = is(0).asInstanceOf[Id]
    val ta = is(1).asInstanceOf[Text]
    val soa = is(2).asInstanceOf[SentenceOffsets]
    val stoa = is(3).asInstanceOf[SentenceTokenOffsets]
    val toka = is(4).asInstanceOf[Tokens]
    val toa = is(5).asInstanceOf[TokenOffsets]
    val la = is(6).asInstanceOf[Lemmas]
    val posa = is(7).asInstanceOf[Poss]
    val nertaga = is(8).asInstanceOf[NerTags]
    val sdepa = is(9).asInstanceOf[SentenceDependencies]

    for (sentNum <- 0 until soa.size) {
      var columns = new Array[String](10)

      val s_stoa = stoa(sentNum)

      val outline = List(
        id,
        sentNum.toString,
        ta.substring(soa(sentNum)(FROM), soa(sentNum)(TO)),
        list2TSVArray(toka.slice(s_stoa(FROM), s_stoa(TO)).toList),
        list2TSVArray(la.slice(s_stoa(FROM), s_stoa(TO)).toList),
        list2TSVArray(posa.slice(s_stoa(FROM), s_stoa(TO)).toList),
        list2TSVArray(nertaga.slice(s_stoa(FROM), s_stoa(TO)).toList),
        intList2TSVArray(toa.slice(s_stoa(FROM), s_stoa(TO)).map {_(FROM) - soa(sentNum)(FROM) }.toList),
        list2TSVArray(sdepa(sentNum).map(_.name).toList),
        intList2TSVArray(sdepa(sentNum).map(_.from).toList)
      )
      writer.append(outline.mkString("\t"))
      writer.newLine()
    }
  }

  /** Construct a Postgres-acceptable array in the TSV format, from a list */
  def list2TSVArray(arr: List[String]) : String = {
    return arr.map( x =>
      // Replace '\' with '\\\\' to be accepted by COPY FROM
      // Replace '"' with '\\"' to be accepted by COPY FROM
      if (x.contains("\\"))
        "\"" + x.replace("\\", "\\\\\\\\").replace("\"", "\\\\\"") + "\""
      else
        "\"" + x + "\""
    ).mkString("{", ",", "}")
  }

  def intList2TSVArray(arr: List[Int]) : String = {
    return arr.map( x =>
      "" + x
    ).mkString("{", ",", "}")
  }

  def string2TSVString(str: String) : String = {
    if (str.contains("\\"))
      str.replace("\\", "\\\\")
    else
      str
  }

  def close =
    writer.close
}