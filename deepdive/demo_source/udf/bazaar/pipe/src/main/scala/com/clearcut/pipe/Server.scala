package com.clearcut.pipe

import java.io._

import com.clearcut.pipe.annotator._
import com.clearcut.pipe.io.{TsvWriter, TsvReader, ColumnWriter, ColumnReader}
import org.http4s._
import org.http4s.dsl._
import org.http4s.server.HttpService
import org.http4s.server.jetty.JettyBuilder
import scala.collection.mutable.ListBuffer
import scala.io.Source

class Server(port: Integer) {

  val route = HttpService {
    case req @ GET -> Root =>
      Ok("Hello. I can parse stuff. Just POST the text to me.\n")

    case req @ POST -> Root =>
      // WARNING: when request body is empty, http4s seems to hang here
      val content = new String(req.body.runLog.run.reduce(_ ++ _).toArray, Charset.`UTF-8`.nioCharset)

      val lines = ListBuffer[String]()

      val annotators:Array[Annotator[_,_]] = Array(new SimpleStanfordPipeline)

      val reader = new TsvReader(inSource = Source.fromString("id\t" + content.replace("\t", " ").replace("\n", " ") + "\n"))
      val baos = new ByteArrayOutputStream
      val writer = new TsvWriter(outWriter = new BufferedWriter(new OutputStreamWriter(baos, "utf-8")))
      val errors = new BufferedWriter(new PrintWriter(new OutputStreamWriter(System.err, "utf-8")))

      Main.run(annotators, reader, writer, errors)

      reader.close
      writer.close

      Ok(baos.toString("utf-8"))
  }

  def run() = {
    JettyBuilder
      .mountService(route, "")
      .bindHttp(port)
      .run
      .awaitShutdown()
  }

}