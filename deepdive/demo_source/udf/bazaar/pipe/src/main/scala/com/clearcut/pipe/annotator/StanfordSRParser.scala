package com.clearcut.pipe.annotator

// StanfordSRParser is very fast, but needs A LOT of memory
// ~ 4GB per thread
// with less memory it becomes very slow

import java.util.Properties

import com.clearcut.pipe.model._
import edu.stanford.nlp.ling.CoreAnnotations.{SentenceIndexAnnotation, SentencesAnnotation}
import edu.stanford.nlp.pipeline.{Annotation => StAnnotation, AnnotatorFactories}
import edu.stanford.nlp.trees.Tree
import edu.stanford.nlp.trees.TreeCoreAnnotations.TreeAnnotation

import scala.collection.JavaConversions._

class StanfordSRParser extends Annotator[(Text,SentenceOffsets,SentenceTokenOffsets,TokenOffsets,Tokens,Poss),
  (Parses,SentenceDependencies)] {

  override def setProperties(p:Properties) {
    super.setProperties(p)
    p.setProperty("annotators", "tokenize,ssplit")
    p.put("parse.maxlen", "100")
    p.put("parse.model", "edu/stanford/nlp/models/srparser/englishSR.ser.gz")
    p.put("threads", "1") // Should use extractor-level parallelism
  }

  @transient lazy val stanfordAnnotator =
    AnnotatorFactories.parse(properties, StanfordUtil.annotatorImplementations).create()

	override def annotate(in:(Text,SentenceOffsets,SentenceTokenOffsets,TokenOffsets,Tokens,Poss)):
		(Parses,SentenceDependencies) = {
		val (t,soa,stoa,toa,to,poa) = in
    val stanAnn = new StAnnotation(t)
    StanfordTokenizer.toStanford(t, toa, to, stanAnn)
    StanfordSentenceSplitter.toStanford(soa, null, stanAnn)
    StanfordPOSTagger.toStanford(poa, stanAnn)

    // NOTE: stanford parser may take too long for all sentences of a document
		// if we run this on Hadoop/Spark, we must parse sentence by sentence and
		// then report progress using
    //if (reporter != null) reporter.incrementCounter();

    stanfordAnnotator.annotate(stanAnn)

    val pa = StanfordSRParser.fromStanford(stanAnn)
    val da = StanfordDependencyExtractor.fromStanford(stanAnn)
    (pa, da)
	}
}

object StanfordSRParser {
  def toStanford(from:Parses, to:StAnnotation):Unit = {
		val l = from
		val sentences = to.get(classOf[SentencesAnnotation])
		for (i <- 0 until l.size) {
			var tree:Tree = null
			if (l(i) != null)
				tree = Tree.valueOf(l(i))
			sentences.get(i).set(classOf[TreeAnnotation], tree)
			sentences.get(i).set(classOf[SentenceIndexAnnotation], i.asInstanceOf[Integer])
		}
  }
  
  def fromStanford(from:StAnnotation):Parses = {
		val sentences = from.get(classOf[SentencesAnnotation])
		val l = for (sentence <- sentences) yield {
			val tree = sentence.get(classOf[TreeAnnotation])
			if (tree != null) tree.pennString else null
		}
		l.toArray
  }
}
