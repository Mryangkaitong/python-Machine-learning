package com.clearcut.pipe

import java.io.{BufferedWriter, FileOutputStream, OutputStreamWriter}

import com.clearcut.pipe.annotator.Annotator
import com.clearcut.pipe.io._

object Main extends App {

  // Parse command line options
  case class Config(serverPort: Integer = null,
                    in: String = null,
                    out: String = null,
                    formatIn: String = "column",
                    formatOut: String = "column",
                    documentKey: String = "text",
                    idKey: String = "id",
                    documentCol: Int = 1,
                    idCol: Int = 0,
                    annotators: String = "SimpleStanfordPipeline")

  val optionsParser = new scopt.OptionParser[Config]("Pipe") {
    head("Run CoreNLP annotators and read/write column/json/tsv formats", "0.1")
    head("Input:  column dir, json file, or tsv file")
    head("Output: column files, json file, or tsv file")
    opt[String]("formatIn") action { (x, c) =>
      c.copy(formatIn = x)
    } text("column, json or tsv")
    opt[String]("formatOut") action { (x, c) =>
      c.copy(formatOut = x)
    } text("column, json or tsv")
    opt[String]('v', "jsonValue") action { (x, c) =>
      c.copy(documentKey = x)
    } text("JSON key that contains the document content, for example \"documents.text\"")
    opt[String]('k', "jsonKey") action { (x, c) =>
      c.copy(idKey = x)
    } text("JSON key that contains the document id, for example \"documents.id\"")
    opt[Int]("tsvValue") action { (x, c) =>
      c.copy(documentCol = x)
    } text("Column number that contains the document content, for example 1")
    opt[Int]("tsvKey") action { (x, c) =>
      c.copy(idCol = x)
    } text("Column number that contains the document id, for example 0")
    opt[String]('i', "input") action { (x, c) =>
      c.copy(in = x)
    } text("Input dir (column) or file (json, tsv)")
    opt[String]('o', "output") action { (x, c) =>
      c.copy(out = x)
    } text("Output dir (column) or file (json, tsv)")
    opt[String]('a', "annotators") action { (x, c) =>
      c.copy(annotators = x)
    } text("Comma-separated list of annotators. Default: SimpleStanfordPipeline")
    opt[Int]('p', "serverPort") action { (x, c) =>
      c.copy(serverPort = x)
    } text("Run as an HTTP service")
  }

  val conf = optionsParser.parse(args, Config()) getOrElse {
    throw new IllegalArgumentException
  }

  if (conf.serverPort != null) {
    Console.println("Listening on port " + conf.serverPort + "...")
    new Server(conf.serverPort).run()
    System.exit(0)
  }

  val errors = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(conf.out + ".errors")))

  val annotators:Array[Annotator[_,_]] = conf.annotators.split(",").map (s =>
      Class.forName("com.clearcut.pipe.annotator." + s.trim).newInstance().asInstanceOf[Annotator[_,_]])

  // load configuration properties from properties file
  if (new java.io.File("config.properties").exists) {
    println("config.properties exists")
    val prop = new java.util.Properties()
    val fromFile = new java.io.FileReader("config.properties")
    prop.load(fromFile)
    fromFile.close
    for (ann <- annotators)
      ann.setProperties(prop)
  }

  val reader:Reader = conf.formatIn match {
    case "column" => new ColumnReader(conf.in)
    case "json" => new JsonReader(conf.in, conf.idKey, conf.documentKey)
    case "tsv" => new TsvReader(conf.in, conf.idCol, conf.documentCol)
  }

  val writer:Writer = conf.formatOut match {
    case "column" => new ColumnWriter(conf.out)
    case "json" => new JsonWriter(conf.out)
    case "tsv" => new TsvWriter(conf.out)
  }

  run(annotators, reader, writer, errors)

  writer.close
  reader.close
  errors.close

  def run(annotators:Array[Annotator[_,_]], reader:Reader, writer:Writer, errors:BufferedWriter) = {
    val schema = Schema.extendSchema(reader.getSchema, annotators)
    val indices = annotators.map(a => Schema.defaultAnnotationIndices(schema, a.requires))
    writer.setSchema(schema)

    for (t <- reader) {
      var all = t
      for ((a, i) <- annotators.zip(indices)) {
        val input = i.map(index => all(index))
        all = all ++ a.annotateUnsafe(input:_*)
      }
      writer.write(all)
    }
  }

}
