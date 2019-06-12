package com.clearcut.pipe.annotator

import scala.collection.JavaConversions._
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation
import edu.stanford.nlp.pipeline.{StanfordCoreNLP, Annotation}
import java.util.Properties
import com.clearcut.pipe.model._
import java.util.regex._
import org.jsoup.Jsoup
import org.jsoup.safety._

class ExtendedCleanHtmlStanfordPipeline extends Annotator[(Text), (Html, SentenceOffsets, TokenOffsets, Tokens, Poss, NerTags, Lemmas,
  SentenceDependencies, Parses, TrueCases, SentenceTokenOffsets)] {

  override def setProperties(p:Properties) {
    super.setProperties(p)
    properties.put("annotators", "tokenize, cleanxml, ssplit, pos, lemma, ner, parse, truecase")
    properties.put("clean.xmltags", ".*")
    properties.put("parse.maxlen", "100")
    properties.put("parse.model", "edu/stanford/nlp/models/srparser/englishSR.ser.gz")
    properties.put("truecase.model", "edu/stanford/nlp/models/truecase/truecasing.fast.qn.ser.gz")
    properties.put("threads", "1") // Should use extractor-level parallelism
    properties.put("clean.allowflawedxml", "true")
    properties.put("clean.sentenceendingtags", "p|br|div|li|ul|ol|h1|h2|h3|h4|h5|blockquote|section|article")
  }
  
  @transient lazy val pipeline = new StanfordCoreNLP(properties)

  val stripHtml = Pattern.compile("<\\/?a|A[^>]*>")

  override def annotate(t:Text):(Html, SentenceOffsets, TokenOffsets, Tokens, Poss, NerTags, Lemmas, SentenceDependencies, Parses, TrueCases, SentenceTokenOffsets) = {

    // clean up Html
    var text = extractCleanHtml(t)

    // Temporary fix for bug where brackets are being incorrectly treated as punct
    // and somehow this messes up the whole dep parse -> change them to round braces
    text = text.replaceAll( """\[""", "(").replaceAll( """\]""", ")")

    var stanAnn = new Annotation(text)
    try {
      pipeline.annotate(stanAnn)
    
    } catch {
      // If our pipeline still fails on this input, we return an empty tuple.
      case e:Exception =>
         System.err.println(text)
         e.printStackTrace(System.err)
         System.err.flush()
         return (text, Array[Offsets](), Array[Offsets](), Array[String](),           Array[String](), Array[String](), Array[String](), Array[Array[Dependency]](), Array[String](), Array[String](), Array[Offsets]())  
    }

    val (toa, to) = StanfordTokenizer.fromStanford(stanAnn)
    val poss = StanfordPOSTagger.fromStanford(stanAnn)
    val nertags = StanfordNERTagger.fromStanford(stanAnn)
    val lemmas = StanfordLemmatizer.fromStanford(stanAnn)
    val deps = StanfordDependencyExtractor.fromStanford(stanAnn)
    val (so, sto) = StanfordSentenceSplitter.fromStanford(stanAnn)
    val pa = StanfordSRParser.fromStanford(stanAnn)
    val tcs = StanfordTrueCaseAnnotator.fromStanford(stanAnn)

    (text, so, toa, to, poss, nertags, lemmas, deps, pa, tcs, sto)
  }

  def extractCleanHtml(html:String):String = {
    val doc = Jsoup.parseBodyFragment(html).body()
    doc.html()
  }
}
