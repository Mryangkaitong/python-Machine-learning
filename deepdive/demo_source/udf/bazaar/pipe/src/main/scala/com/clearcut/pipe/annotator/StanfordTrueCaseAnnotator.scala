package com.clearcut.pipe.annotator

import com.clearcut.pipe.model._
import scala.collection.JavaConversions._
import edu.stanford.nlp.ling.CoreAnnotations
import edu.stanford.nlp.pipeline.{Annotation => StAnnotation, AnnotatorFactories}
import java.util._

/** Wraps CoreNLP TrueCaseAnnotator as an Annotator. */
class StanfordTrueCaseAnnotator extends Annotator[(Text,TokenOffsets,Tokens,SentenceOffsets),(TrueCases)] {
  
  @transient lazy val stanfordAnnotator =
    AnnotatorFactories.truecase(properties, StanfordUtil.annotatorImplementations).create()

  override def annotate(in:(Text,TokenOffsets,Tokens,SentenceOffsets)):TrueCases = {
    val (t, toa, to, soa) = in
    val stanAnn = new edu.stanford.nlp.pipeline.Annotation(t)
    StanfordTokenizer.toStanford(t, toa, to, stanAnn)
    StanfordSentenceSplitter.toStanford(soa, null, stanAnn)

    stanfordAnnotator.annotate(stanAnn)

    StanfordTrueCaseAnnotator.fromStanford(stanAnn)
  }
}

/** Stanford model mappings for POS tags. */
object StanfordTrueCaseAnnotator {
  def toStanford(from:TrueCases, to:StAnnotation):Unit = {
    val li = to.get(classOf[CoreAnnotations.TokensAnnotation])
    for (i <- 0 until li.size) {
      val tc = from(i)
      li.get(i).set(classOf[CoreAnnotations.TrueCaseAnnotation], tc)
    }
  }

  def fromStanford(from:StAnnotation):TrueCases = {
    val tokens = from.get(classOf[CoreAnnotations.TokensAnnotation])
    tokens.map(_.getString(classOf[CoreAnnotations.TrueCaseAnnotation])).toArray
  }
}
