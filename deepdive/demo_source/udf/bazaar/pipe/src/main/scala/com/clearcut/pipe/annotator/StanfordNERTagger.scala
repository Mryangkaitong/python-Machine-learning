package com.clearcut.pipe.annotator

import com.clearcut.pipe.model._
import scala.collection.JavaConversions._
import edu.stanford.nlp.ling.CoreAnnotations
import edu.stanford.nlp.pipeline.{Annotation => StAnnotation, AnnotatorFactories}
import com.clearcut.pipe.model._
import java.util._

/** Wraps CoreNLP NER Tagger as an Annotator. */
class StanfordNERTagger extends Annotator[(Text,TokenOffsets,Tokens,SentenceOffsets,Lemmas,Poss), (NerTags)] {

  @transient lazy val stanfordAnnotator =
    AnnotatorFactories.nerTag(properties, StanfordUtil.annotatorImplementations).create()

  override def annotate(in:(Text,TokenOffsets,Tokens,SentenceOffsets,Lemmas,Poss)): NerTags = {
    val (t, toa, to, soa, la, pa) = in
    val stanAnn = new StAnnotation(t)
    StanfordTokenizer.toStanford(t, toa, to, stanAnn)
    StanfordSentenceSplitter.toStanford(soa, null, stanAnn)
    StanfordPOSTagger.toStanford(pa, stanAnn)
    StanfordLemmatizer.toStanford(la, stanAnn)

    stanfordAnnotator.annotate(stanAnn)

    StanfordNERTagger.fromStanford(stanAnn)
  }
}

/** Stanford model mappings for NER. */
object StanfordNERTagger {
  def toStanford(from:NerTags, to:StAnnotation):Unit = {
    val li = to.get(classOf[CoreAnnotations.TokensAnnotation])
    for (i <- 0 until li.size) {
      val ner = from(i)
      li.get(i).setNER(ner)
    }
  }
  
  def fromStanford(from:StAnnotation):NerTags = {
    val tokens = from.get(classOf[CoreAnnotations.TokensAnnotation])
    val li = for (cl <- tokens) yield {
      // there may be *NL* tokens outside sentences; the lemmatizer didn't reach
      // these, so set these manually to *NL*, so that serialization is OK
      val n = cl.ner
      if (n != null) n else "O"
    }
    li.toArray
  }
}
