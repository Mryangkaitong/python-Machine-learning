package com.clearcut.pipe.annotator

import java.util.Properties
import com.clearcut.pipe.model._
import scala.collection.JavaConversions.asScalaBuffer
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation
import edu.stanford.nlp.pipeline.{Annotation => StAnnotation, AnnotatorFactories}

/** Wraps CoreNLP Lemmatizer as an Annotator. */
class StanfordLemmatizer extends Annotator[(Text, Poss, SentenceOffsets, TokenOffsets, Tokens), (Lemmas)] {

	@transient lazy val stanfordAnnotator =
		AnnotatorFactories.lemma(properties, StanfordUtil.annotatorImplementations).create()

  override def annotate(in:(Text, Poss, SentenceOffsets, TokenOffsets, Tokens)):Lemmas = {
		val (t, poa, soa, toa, to) = in
		val stanAnn = new StAnnotation(t)
		StanfordTokenizer.toStanford(t, toa, to, stanAnn)
		StanfordSentenceSplitter.toStanford(soa, null, stanAnn)
		StanfordPOSTagger.toStanford(poa, stanAnn)

		stanfordAnnotator.annotate(stanAnn)

		StanfordLemmatizer.fromStanford(stanAnn)
  }
}

/** Stanford model mappings for lemmas. */
object StanfordLemmatizer {
	def toStanford(from:Lemmas, to:StAnnotation):Unit = {
		val li = to.get(classOf[TokensAnnotation])
		for (i <- 0 until from.size) {
			val lemma = from(i)
			li.get(i).setLemma(lemma)
		}
	}

	def fromStanford(from:StAnnotation):Lemmas = {
		val tokens = from.get(classOf[TokensAnnotation])
		val li = for (cl <- tokens) yield {
			// there may be *NL* tokens outside sentences; the lemmatizer didn't reach
			// these, so set these manually to *NL*, so that serialization is OK
			var l = cl.lemma()
			if (l == null) l = "*NL*"
			l
		}
		li.toArray
	}
}
