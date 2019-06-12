package com.clearcut.pipe.annotator

import edu.stanford.nlp.pipeline.AnnotatorImplementations

object StanfordUtil {

  lazy val annotatorImplementations =
    new AnnotatorImplementations

}
