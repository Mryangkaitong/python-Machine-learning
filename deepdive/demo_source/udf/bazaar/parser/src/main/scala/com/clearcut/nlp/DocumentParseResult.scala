package com.clearcut.nlp

case class SentenceParseResult(
	sentence: String,
	words: List[String],
	lemma: List[String],
  	pos_tags: List[String],
  	ner_tags: List[String],
  	offsets: List[Int],
  	dep_labels: List[String], 
  	dep_parents: List[Int],
  	collapsed_deps: List[String]
)

case class DocumentParseResult(
	sentences: List[SentenceParseResult]
)
