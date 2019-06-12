package com.clearcut.pipe

import com.clearcut.pipe.io.Json

/** Set of our cross-language, minimalist schema */
package object model {
  type Html = String
  type Coreferences = Array[CoreferenceChain]
  type Dependencies = Array[Dependency]
  type Id = String
  type Lemmas = Array[String]
  type Mentions = Array[Mention]
  type Ners = Array[NamedEntity]
  type NerTags = Array[String]
  type Offsets = Array[Int]
  type Parses = Array[String]
  type Poss = Array[String]
  type SentenceDependencies = Array[Array[Dependency]]
  type SentenceOffsets = Array[Offsets]
  type SentenceTokenOffsets = Array[Offsets]
  type Text = String
  type TextFragments = Array[TextFragment]
  type TextMappings = Array[TextMapping]
  type TokenOffsets = Array[Offsets]
  type Tokens = Array[String]
  type TrueCases = Array[String]

  /* Constants used for offsets */
  val FROM = 0
  val TO = 1

  def print(s: Schema, arr: AnyRef*) =
    for ((name, ann) <- s.annTyps.zip(arr))
      println(name + " : " + Json.write(arr))

  def lowerFirst(s:String) =
    if (s == null || s.length < 1) s
    else s.charAt(0).toLower + s.substring(1)

  def upperFirst(s:String) =
    if (s == null || s.length < 1) s
    else s.charAt(0).toUpper + s.substring(1)


  /* Auxiliary sub-types used above */

  case class CoreferenceChain
  (
    chainNum: Int = -1,
    representativeMentionNum: Int = -1,
    mentionNums: Array[Int] = Array()
    )

  case class Dependency
  (
    name: String,
    from: Int,
    to: Int
    )

  case class NamedEntity
  (
    typ:String,
    offsets:Offsets,
    head:Int = -1
    )


  case class Mention
  (
    mentionNum:Int = -1,
    head:Int = -1,  // token offset from begin of document
    tokenOffsets:Offsets,
    mentionTyp:Byte = -1, //PRONOMINAL, NOMINAL, PROPER, UNKNOWN
    number:Byte = -1,     //SINGULAR, PLURAL, UNKNOWN
    gender:Byte = -1,     //MALE, FEMALE, NEUTRAL, UNKNOWN
    animacy:Byte = -1     //ANIMATE, INANIMATE, UNKNOWN
    )

  object Mention {
    val UNKNOWN = -1.toByte

    // mention types
    val PRONOMINAL = 0.toByte
    val NOMINAL = 1.toByte
    val PROPER = 2.toByte
    val LIST = 3.toByte

    // numbers
    val SINGULAR = 0.toByte
    val PLURAL = 1.toByte

    // genders
    val MALE = 0.toByte
    val FEMALE = 1.toByte
    val NEUTRAL = 2.toByte

    // animacy
    val ANIMATE = 0.toByte
    val INANIMATE = 1.toByte

    // need bidirectional mappings for stanford conversions

    def typeToByte(s:String) = s match {
      case "PRONOMINAL" => PRONOMINAL
      case "NOMINAL" => NOMINAL
      case "PROPER" => PROPER
      case "LIST" => LIST
      case "UNKNOWN" => UNKNOWN
    }

    def typeFromByte(b:Byte) = b match {
      case PRONOMINAL => "PRONOMINAL"
      case NOMINAL => "NOMINAL"
      case PROPER => "PROPER"
      case LIST => "LIST"
      case UNKNOWN => "UNKNOWN"
    }

    def numberToByte(s:String) = s match {
      case "SINGULAR" => SINGULAR
      case "PLURAL" => PLURAL
      case "UNKNOWN" => UNKNOWN
    }

    def numberFromByte(b:Byte) = b match {
      case SINGULAR => "SINGULAR"
      case PLURAL => "PLURAL"
      case UNKNOWN => "UNKNOWN"
    }

    def genderToByte(s:String) = s match {
      case "MALE" => MALE
      case "FEMALE" => FEMALE
      case "NEUTRAL" => NEUTRAL
      case "UNKNOWN" => UNKNOWN
    }

    def genderFromByte(b:Byte) = b match {
      case MALE => "MALE"
      case FEMALE => "FEMALE"
      case NEUTRAL => "NEUTRAL"
      case UNKNOWN => "UNKNOWN"
    }

    def animacyToByte(s:String) = s match {
      case "ANIMATE" => ANIMATE
      case "INANIMATE" => INANIMATE
      case "UNKNOWN" => UNKNOWN
    }

    def animacyFromByte(b:Byte) = b match {
      case ANIMATE => "ANIMATE"
      case INANIMATE => "INANIMATE"
      case UNKNOWN => "UNKNOWN"
    }
  }

  case class TextFragment
  (
    typ:String,
    offsets:Offsets,
    extract:Boolean
    )

  case class TextMapping
  (
    documentID:Int,
    beginText:Int,
    beginSource:Int,
    length:Int
    )
}
