package com.clearcut.pipe.annotator

import java.util.{ArrayList, Properties}
import com.clearcut.pipe.model.{Offsets, Text, Tokens, TokenOffsets}
import edu.stanford.nlp.ling.{CoreAnnotations, CoreLabel}
import edu.stanford.nlp.pipeline.{Annotation => StAnnotation, AnnotatorFactories}
import scala.collection.JavaConversions._
import scala.collection.JavaConverters._

/** Wraps CoreNLP Tokenizer as an Annotator. */
class StanfordTokenizer extends Annotator[Text,(TokenOffsets,Tokens)] {

  @transient lazy val stanfordAnnotator =
    AnnotatorFactories.tokenize(properties, StanfordUtil.annotatorImplementations).create()

  override def annotate(t:(Text)):(TokenOffsets, Tokens) = {
    val stanAnn = new StAnnotation(t)
    stanfordAnnotator.annotate(stanAnn)
    StanfordTokenizer.fromStanford(stanAnn)
  }
}

/** Stanford model mappings for tokens. */
object StanfordTokenizer {
  def toStanford(text:Text, tokenOffsets:TokenOffsets, tokens:Tokens, to:StAnnotation):Unit = {
    val li = for (i <- 0 until tokens.size) yield {
      val to = tokenOffsets(i)
      val cl = new CoreLabel
      cl.setValue(tokens(i))
      cl.setWord(tokens(i))
      cl.setOriginalText(text.substring(to(0), to(1)))
      cl.set(classOf[CoreAnnotations.CharacterOffsetBeginAnnotation], to(0).asInstanceOf[Integer])
      cl.set(classOf[CoreAnnotations.CharacterOffsetEndAnnotation], to(1).asInstanceOf[Integer])
      cl
    }
    to.set(classOf[CoreAnnotations.TokensAnnotation], li.asJava)
  }

  def fromStanford(from:StAnnotation):(TokenOffsets, Tokens) = {
    val tokens = from.get(classOf[CoreAnnotations.TokensAnnotation])
    val li = tokens.map(cl => Array(cl.beginPosition, cl.endPosition))
    val ti = tokens.map(_.word)
    (li.toArray, ti.toArray)
  }
}
