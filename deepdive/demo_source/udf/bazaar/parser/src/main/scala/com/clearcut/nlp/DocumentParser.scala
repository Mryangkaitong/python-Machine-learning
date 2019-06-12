package com.clearcut.nlp

import edu.stanford.nlp.ling.CoreAnnotations._
import edu.stanford.nlp.pipeline._
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.{CollapsedCCProcessedDependenciesAnnotation, CollapsedDependenciesAnnotation}

// import edu.stanford.nlp.dcoref.CorefCoreAnnotations.CorefChainAnnotation
import java.util.Properties

import scala.collection.JavaConversions._


class DocumentParser(props: Properties) {

  val pipeline = new StanfordCoreNLP(props)

  def parseDocumentString(doc: String) = {

    // Temporary fix for bug where brackets are being incorrectly treated as punct
    // and somehow this messes up the whole dep parse -> change them to round braces
    val doc2 = doc.replaceAll("""\[""", "(").replaceAll("""\]""", ")")

    val document = new Annotation(doc2)
    pipeline.annotate(document)
    // val dcoref = document.get(classOf[CorefChainAnnotation])
    val sentences = document.get(classOf[SentencesAnnotation])

    val sentenceResults = sentences.zipWithIndex.map { case(sentence, sentIdx) =>
      val content = sentence.toString
      val tokens = sentence.get(classOf[TokensAnnotation])
      val wordList = tokens.map(_.get(classOf[TextAnnotation]))
      val posList = tokens.map(_.get(classOf[PartOfSpeechAnnotation]))
      val nerList = tokens.map(_.get(classOf[NamedEntityTagAnnotation]))
      val lemmaList = tokens.map(_.get(classOf[LemmaAnnotation]))
      val offsetList = tokens.map(_.get(classOf[CharacterOffsetBeginAnnotation]).intValue)

      // This kind of dep paths seem to be a tree. Need CoreNLP guys to confirm.
      // Ce has been using this all along.
      val depCollapsedPaths = sentence.get(classOf[CollapsedDependenciesAnnotation]).edgeIterable
      val depLabels = Array.fill(tokens.size)("")
      val depParents = Array.fill(tokens.size)(0)
      for (path <- depCollapsedPaths) {
        depLabels(path.getTarget.index - 1) = path.getRelation.toString
        depParents(path.getTarget.index - 1) = path.getSource.index
      }

      // This kind of dep paths may have cycles.
      val depCCPPaths = sentence.get(classOf[CollapsedCCProcessedDependenciesAnnotation]).edgeIterable
      val ccpPathTriples = for(path <- depCCPPaths) yield
        List(path.getSource.index, path.getRelation, path.getTarget.index).mkString(",")
      
      SentenceParseResult(
        content, 
        wordList.toList, 
        lemmaList.toList, 
        posList.toList,
        nerList.toList,
        offsetList.toList,
        depLabels.toList,
        depParents.toList,
        ccpPathTriples.toList
      )
    }

    DocumentParseResult(sentenceResults.toList) 
  }

  /**
    Construct a Postgres-acceptable array in the TSV format, from a list
  */
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

  // NOTE: an alternative would be to quote the field correctly
  // http://stackoverflow.com/questions/3089077/new-lines-in-tab-delimited-or-comma-delimtted-output
  def replaceChars(str: String) : String = {
    str.replace("\n", " ").replace("\t", " ")
  }

}
