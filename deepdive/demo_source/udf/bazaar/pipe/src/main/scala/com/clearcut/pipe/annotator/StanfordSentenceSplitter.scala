package com.clearcut.pipe.annotator

import java.util.ArrayList
import java.util.Properties

import com.clearcut.pipe.model._

import scala.collection.JavaConversions.asScalaBuffer
import scala.collection.mutable.ArrayBuffer
import scala.util.control.Breaks.break
import scala.util.control.Breaks.breakable

import edu.stanford.nlp.ling.CoreAnnotations.CharacterOffsetBeginAnnotation
import edu.stanford.nlp.ling.CoreAnnotations.CharacterOffsetEndAnnotation
import edu.stanford.nlp.ling.CoreAnnotations.SentenceIndexAnnotation
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation
import edu.stanford.nlp.ling.CoreAnnotations.TextAnnotation
import edu.stanford.nlp.ling.CoreAnnotations.TokenBeginAnnotation
import edu.stanford.nlp.ling.CoreAnnotations.TokenEndAnnotation
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation
import edu.stanford.nlp.ling.CoreLabel
import edu.stanford.nlp.pipeline.{Annotation => StAnnotation, AnnotatorFactories}
import edu.stanford.nlp.util.CoreMap

class StanfordSentenceSplitter extends Annotator[(Text,TokenOffsets,Tokens), (SentenceOffsets,SentenceTokenOffsets)] {

	@transient lazy val stanfordAnnotator =
		AnnotatorFactories.sentenceSplit(properties, StanfordUtil.annotatorImplementations).create()

	override def annotate(in:(Text,TokenOffsets,Tokens)): (SentenceOffsets, SentenceTokenOffsets) = {
		val (t, td, to) = in
		val sssFrags = new StanfordSentenceSplitterWithFrags
		val fa = Array(TextFragment("extract", Array(0, t.size), true))
		sssFrags.annotate(t, fa, td, to)
	}
}

object StanfordSentenceSplitter {
  
  // second argument can be null, in which case we compute the token offsets
  def toStanford(sep:SentenceOffsets, stoa:SentenceTokenOffsets, to:StAnnotation) {
    val tokens = to.get(classOf[TokensAnnotation])
	val text = to.get(classOf[TextAnnotation])
	
	val sentences = new ArrayList[CoreMap]()
	var sentNum = 0
	var nextTok = 0
	for (i <- 0 until sep.size) {
	  val s = sep(i)
			
	  val sentenceText = text.substring(s(FROM), s(TO))

	  var beginTok = -1
	  var endTok = -1
	  if (stoa != null) {
	    val sto = stoa(i)
	    beginTok = sto(FROM)
	    endTok = sto(TO)
	  } else {
	    while (nextTok < tokens.size && tokens.get(nextTok).beginPosition < s(FROM)) nextTok += 1
	    beginTok = nextTok
	    endTok = beginTok
	    while (endTok < tokens.size && tokens.get(endTok).endPosition <= s(TO)) endTok += 1
	    nextTok = endTok
	  }
	  
	  val toks = to.get(classOf[TokensAnnotation]).subList(beginTok, endTok)
			
	  val sentence = new StAnnotation(sentenceText)
	  sentence.set(classOf[SentenceIndexAnnotation], sentNum.asInstanceOf[Integer])
	  sentence.set(classOf[CharacterOffsetBeginAnnotation], s(FROM).asInstanceOf[Integer])
	  sentence.set(classOf[CharacterOffsetEndAnnotation], s(TO).asInstanceOf[Integer])
	  sentence.set(classOf[TokensAnnotation], toks)
	  sentence.set(classOf[TokenBeginAnnotation], beginTok.asInstanceOf[Integer])
	  sentence.set(classOf[TokenEndAnnotation], endTok.asInstanceOf[Integer])
	  sentences.add(sentence)
	  sentNum += 1
	}
	to.set(classOf[SentencesAnnotation], sentences)
  }
	
  def fromStanford(from:StAnnotation):(SentenceOffsets, SentenceTokenOffsets) = {
	val sentences = from.get(classOf[SentencesAnnotation])		
	val cli = new ArrayBuffer[Offsets](sentences.size)
	val tli = new ArrayBuffer[Offsets](sentences.size)
	for (sentence <- sentences) {
	  cli += Array(sentence.get(classOf[CharacterOffsetBeginAnnotation]),
	      sentence.get(classOf[CharacterOffsetEndAnnotation]))
	      
	  tli += Array(sentence.get(classOf[TokenBeginAnnotation]),
	      sentence.get(classOf[TokenEndAnnotation]))
	}
	(cli.toArray, tli.toArray)
  }
}

// a sentence splitter that preserves frags boundaries
class StanfordSentenceSplitterWithFrags extends Annotator[(Text,TextFragments,TokenOffsets,Tokens),
	(SentenceOffsets,SentenceTokenOffsets)] {

  //val properties = new Properties()
  //@transient lazy val stanfordAnnotator = StanfordHelper.getAnnotator(properties, "ssplit")
	@transient lazy val stanfordAnnotator =
		AnnotatorFactories.sentenceSplit(properties, StanfordUtil.annotatorImplementations).create()

  override def annotate(in:(Text,TextFragments,TokenOffsets,Tokens)):(SentenceOffsets, SentenceTokenOffsets) = {
		val (t,fa, td, to) = in
		// create Stanford annotation with relevant contents
		val stanAnn = new StAnnotation(t)
		StanfordTokenizer.toStanford(t, td, to, stanAnn)

		val docSnts = new ArrayList[CoreMap]()
		val li = stanAnn.get(classOf[TokensAnnotation])
		var sentNum = 0

		// look at every fragment separately
		for (frag <- fa) {
			val raw = t.substring(frag.offsets(FROM), frag.offsets(TO))

			// get tokens annotations
			val sli = new ArrayList[CoreLabel]()
			var firstToken = -1
			for (i <- 0 until li.size) {
				val cl = li.get(i)
				if (cl.get(classOf[CharacterOffsetBeginAnnotation]) >= frag.offsets(FROM) &&
						cl.get(classOf[CharacterOffsetEndAnnotation]) <= frag.offsets(TO)) {
					if (firstToken == -1) firstToken = i

					val ncl = new CoreLabel()
					ncl.setValue(cl.value)
					ncl.setWord(cl.word)
					ncl.setOriginalText(cl.originalText)
					ncl.set(classOf[CharacterOffsetBeginAnnotation], new Integer(cl.beginPosition - frag.offsets(FROM)))
					ncl.set(classOf[CharacterOffsetEndAnnotation], new Integer(cl.endPosition - frag.offsets(FROM)))
					sli.add(ncl)
				}
			}
			val fragStanAnn = new StAnnotation(raw)

			fragStanAnn.set(classOf[TokensAnnotation], sli)

			// now run it
			stanfordAnnotator.annotate(fragStanAnn)

			for (sentence <- fragStanAnn.get(classOf[SentencesAnnotation])) {
			var sentenceTokens = sentence.get(classOf[TokensAnnotation])

			// 1. remove newlines at beginning or end of sentence
			var newStart = 0
			var newEnd = sentenceTokens.size
			breakable {
				for (i <- 0 until sentenceTokens.size)
					if (sentenceTokens.get(i).value().equals("*NL*")) newStart += 1 else break
			}
			breakable {
				for (i <- sentenceTokens.size-1 to 0 by -1)
					if (sentenceTokens.get(i).value().equals("*NL*")) newEnd -= 1 else break
			}

			// TODO: special case: no tokens left??
			if (newEnd > newStart) {
				//if (newStart == 0 && newEnd == sentenceTokens.size()) {
				//  snts.add(sentence);
				//  continue;
				//}
				//System.out.println(newStart)
				sentenceTokens = sentenceTokens.subList(newStart, newEnd)
				sentence.set(classOf[SentenceIndexAnnotation], sentNum.asInstanceOf[Integer])
				sentence.set(classOf[TokensAnnotation], sentenceTokens)
				sentence.set(classOf[TokenBeginAnnotation],
					new Integer(sentence.get(classOf[TokenBeginAnnotation]) + newStart))
				sentence.set(classOf[TokenEndAnnotation],
					new Integer(sentence.get(classOf[TokenBeginAnnotation]) + sentenceTokens.size))
				sentence.set(classOf[CharacterOffsetBeginAnnotation],
					new Integer(sentenceTokens.get(0).get(classOf[CharacterOffsetBeginAnnotation])))
				sentence.set(classOf[CharacterOffsetEndAnnotation],
					new Integer(sentenceTokens.get(sentenceTokens.size-1).get(classOf[CharacterOffsetEndAnnotation])))

				// 2. correct for document token offsets
				for (cl <- sentenceTokens) {
					cl.set(classOf[CharacterOffsetBeginAnnotation],
						new Integer(cl.get(classOf[CharacterOffsetBeginAnnotation]) + frag.offsets(FROM)))
					cl.set(classOf[CharacterOffsetEndAnnotation],
						new Integer(cl.get(classOf[CharacterOffsetEndAnnotation]) + frag.offsets(FROM)))
				}
				sentence.set(classOf[CharacterOffsetBeginAnnotation],
					new Integer(sentence.get(classOf[CharacterOffsetBeginAnnotation]) + frag.offsets(FROM)))
				sentence.set(classOf[CharacterOffsetEndAnnotation],
					new Integer(sentence.get(classOf[CharacterOffsetEndAnnotation]) + frag.offsets(FROM)))
				sentence.set(classOf[TokenBeginAnnotation],
					new Integer(sentence.get(classOf[TokenBeginAnnotation]) + firstToken))
				sentence.set(classOf[TokenEndAnnotation],
					new Integer(sentence.get(classOf[TokenEndAnnotation]) + firstToken))

				docSnts.add(sentence)
				sentNum += 1
			}
			}
			stanAnn.set(classOf[SentencesAnnotation], docSnts)
		}

		StanfordSentenceSplitter.fromStanford(stanAnn)
  }
}
