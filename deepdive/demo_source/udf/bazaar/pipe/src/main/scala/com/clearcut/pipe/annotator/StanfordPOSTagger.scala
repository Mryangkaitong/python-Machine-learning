package com.clearcut.pipe.annotator

import com.clearcut.pipe.model._
import scala.collection.JavaConversions._
import edu.stanford.nlp.ling.CoreAnnotations
import edu.stanford.nlp.pipeline.{Annotation => StAnnotation, AnnotatorFactories}
import java.util._

/** Wraps CoreNLP POS Tagger as an Annotator. */
class StanfordPOSTagger extends Annotator[(Text,TokenOffsets,Tokens,SentenceOffsets),(Poss)] {
  
  @transient lazy val stanfordAnnotator =
    AnnotatorFactories.posTag(properties, StanfordUtil.annotatorImplementations).create()

  override def annotate(in:(Text,TokenOffsets,Tokens,SentenceOffsets)):Poss = {
    val (t, toa, to, soa) = in
    val stanAnn = new edu.stanford.nlp.pipeline.Annotation(t)
    StanfordTokenizer.toStanford(t, toa, to, stanAnn)
    StanfordSentenceSplitter.toStanford(soa, null, stanAnn)

    stanfordAnnotator.annotate(stanAnn)

    StanfordPOSTagger.fromStanford(stanAnn)
  }
}

/** Stanford model mappings for POS tags. */
object StanfordPOSTagger {
  def toStanford(from:Poss, to:StAnnotation):Unit = {
    val li = to.get(classOf[CoreAnnotations.TokensAnnotation])
    for (i <- 0 until li.size) {
      val pos = from(i)
      li.get(i).set(classOf[CoreAnnotations.PartOfSpeechAnnotation], pos)
    }
  }

  def fromStanford(from:StAnnotation):Poss = {
    val tokens = from.get(classOf[CoreAnnotations.TokensAnnotation])
    tokens.map(_.getString(classOf[CoreAnnotations.PartOfSpeechAnnotation])).toArray
  }
}
