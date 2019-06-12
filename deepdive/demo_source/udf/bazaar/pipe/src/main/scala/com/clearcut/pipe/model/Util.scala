package com.clearcut.pipe.model

object Util {

  val types:Array[Class[_ <: AnyRef]] = Array(
    classOf[Coreferences],
    classOf[Dependencies],
    classOf[Lemmas],
    classOf[Mentions],
    classOf[Ners],
    classOf[NerTags],
    classOf[Offsets],
    classOf[Parses],
    classOf[Poss],
    classOf[SentenceDependencies],
    classOf[SentenceOffsets],
    classOf[SentenceTokenOffsets],
    classOf[Text],
    classOf[TextFragments],
    classOf[TextMappings],
    classOf[TokenOffsets],
    classOf[Tokens],
    classOf[TrueCases]
  )

//  val name2clazz =
//    Map(types.map(t => lowerFirst(t.getSimpleName) -> t):_*)

//  val clazz2name:Map[Class[_ <: AnyRef], String] =
//    name2clazz.map(_.swap)


  val name2clazz = Map(
    "coreferences" -> classOf[Coreferences],
    "dependencies" -> classOf[Dependencies],
    "lemmas" -> classOf[Lemmas],
    "mentions" -> classOf[Mentions],
    "ners" -> classOf[Ners],
    "nerTags" -> classOf[NerTags],
    "parses" -> classOf[Parses],
    "poss" -> classOf[Poss],
    "sentenceDependencies" -> classOf[SentenceDependencies],
    "sentenceOffsets" -> classOf[SentenceOffsets],
    "sentenceTokenOffsets" -> classOf[SentenceTokenOffsets],
    "text" -> classOf[Text],
    "textFragments" -> classOf[TextFragments],
    "textMappings" -> classOf[TextMappings],
    "tokenOffsets" -> classOf[TokenOffsets],
    "tokens" -> classOf[Tokens],
    "trueCases" -> classOf[TrueCases]
  )





  def lowerFirst(s:String) =
    if (s == null || s.length < 1) s
    else s.charAt(0).toLower + s.substring(1)
}
