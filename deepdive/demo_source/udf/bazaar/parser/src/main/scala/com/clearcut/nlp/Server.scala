package com.clearcut.nlp

import org.http4s._
import org.http4s.dsl._
import org.http4s.server.HttpService
import org.http4s.server.jetty.JettyBuilder
import scala.collection.mutable.ListBuffer
import scalaz.stream.Process._


class Server(dp: DocumentParser, port: Integer) {

  val route = HttpService {
    case req @ GET -> Root =>
      Ok("Hello. I can parse stuff. Just POST the text to me.\n")

    case req @ POST -> Root =>
      // WARNING: when request body is empty, http4s seems to hang here
      val content = new String(req.body.runLog.run.reduce(_ ++ _).toArray, Charset.`UTF-8`.nioCharset)

      val lines = ListBuffer[String]()
      dp.parseDocumentString(content).sentences.zipWithIndex
        .foreach { case (sentenceResult, sentence_idx) =>

        val outline = List(
          sentence_idx + 1,
          sentenceResult.sentence,
          dp.list2TSVArray(sentenceResult.words),
          dp.list2TSVArray(sentenceResult.lemma),
          dp.list2TSVArray(sentenceResult.pos_tags),
          dp.list2TSVArray(sentenceResult.ner_tags),
          dp.intList2TSVArray(sentenceResult.offsets),
          dp.list2TSVArray(sentenceResult.dep_labels),
          dp.intList2TSVArray(sentenceResult.dep_parents)
          // dp.list2TSVArray(sentenceResult.collapsed_deps)
        ).mkString("\t")

        lines += outline
      }
      Ok(lines.toList.mkString("\n") + "\n")
  }

  def run() = {
    JettyBuilder
      .mountService(route, "")
      .bindHttp(port)
      .run
      .awaitShutdown()
  }

}
