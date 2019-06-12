package com.clearcut.pipe.annotator

import java.util.List

import com.clearcut.pipe.model.Dependency
import com.clearcut.pipe.model.SentenceDependencies
import edu.stanford.nlp.ling.CoreAnnotations._
import edu.stanford.nlp.ling.{IndexedWord, CoreLabel}
import edu.stanford.nlp.pipeline.{Annotation => StAnnotation}
import edu.stanford.nlp.semgraph.SemanticGraph
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.{BasicDependenciesAnnotation,
  CollapsedCCProcessedDependenciesAnnotation, CollapsedDependenciesAnnotation}
import edu.stanford.nlp.trees.GrammaticalRelation

import scala.collection.JavaConversions.asScalaBuffer
import scala.collection.mutable.ArrayBuffer

object StanfordDependencyExtractor {

  val DEFAULT_DEP_TYPE = "DepCCProcessed"

  val depTypes = Array("DepCollapsed", "DepUncollapsed", "DepCCProcessed")

  def fromStanford(from:StAnnotation, depTyp:String = DEFAULT_DEP_TYPE):SentenceDependencies = {
    val sentences = from.get(classOf[SentencesAnnotation])
    val psl = new ArrayBuffer[Array[Dependency]](sentences.size)
    for (sentence <- sentences) {
      val deps = depTyp match {
        case "DepCollapsed" =>
          sentence.get(classOf[CollapsedDependenciesAnnotation])
        case "DepUncollapsed" =>
          sentence.get(classOf[BasicDependenciesAnnotation])
        case "DepCCProcessed" =>
          sentence.get(classOf[CollapsedCCProcessedDependenciesAnnotation])
      }

      if (deps != null) {
        val edgeSet = deps.edgeListSorted
        val pl = for (e <- edgeSet) yield {
          Dependency(e.getRelation.toString, e.getGovernor.index - 1, e.getDependent.index - 1)
        }
        psl += pl.toArray
      }
    }
    psl.toArray
  }

  def toStanford(depTyp:String, from:SentenceDependencies, to:StAnnotation):Unit = {
    val toks = to.get(classOf[TokensAnnotation])
    val l = to.get(classOf[SentencesAnnotation])
    for (i <- 0 until l.size) {
      val fromIndex = l.get(i).get(classOf[TokenBeginAnnotation])
      val toIndex = l.get(i).get(classOf[TokenEndAnnotation])
      val sntToks = toks.subList(fromIndex, toIndex)

      val sg = toSemanticGraph(sntToks, from(i))

      depTyp match {
        case "DepCollapsed" =>
          l.get(i).set(classOf[CollapsedDependenciesAnnotation], sg)
        case "DepUncollapsed" =>
          l.get(i).set(classOf[BasicDependenciesAnnotation], sg)
        case "DepCCProcessed" =>
          l.get(i).set(classOf[CollapsedCCProcessedDependenciesAnnotation], sg)
      }
    }
  }

  def toSemanticGraph(tokens:List[CoreLabel], deps:Array[Dependency]):SemanticGraph = {
    val sg = new SemanticGraph()
    for (i <- 0 until tokens.size) {
      val index = i+1
      val word = tokens.get(i).value() //getValue();

      //TODO: not setting root
      //(are roots those nodes that have 0 incoming edges)

      val ifl = new IndexedWord(null, 0, index);
      // condition added by me, after "/" as token caused IndexOutOfBounds, maybe TokensAnnotation in wrong token format?
      val wordAndTag = if (word.length > 1) word.split("/") else Array(word)
      ifl.set(classOf[TextAnnotation], wordAndTag(0))
      if (wordAndTag.length > 1) {
        ifl.set(classOf[PartOfSpeechAnnotation], wordAndTag(1))
      }
      sg.addVertex(ifl)
    }
    val vertices = sg.vertexListSorted()

    for (d <- deps) {
      val govId = d.from
      val reln = d.name
      val depId = d.to
      val gov = vertices.get(govId)
      val dep = vertices.get(depId)
      val isExtra = false; //?
      sg.addEdge(gov, dep, GrammaticalRelation.valueOf(reln),
        java.lang.Double.NEGATIVE_INFINITY, isExtra)
    }
    sg
  }
}