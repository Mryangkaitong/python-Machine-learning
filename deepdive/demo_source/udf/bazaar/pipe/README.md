Pipe
====

Lightweight schemas and processing framework for NLP. 

Pipe addresses the following problems: 

* In many DeepDive applications, errors in pre-processing become more relevant as one tries to push up precision and recall. Often no further quality improvement is possible without targeting these errors. 

  An example:
  ```
  $300. 00 per hour
  ```
  Our sentence splitter would break on the period and create two sentences.

  For some extractors we have tried work-arounds by adding complex rules to our extractors which target these errors. In fact, a significant portion of code in our 'rates' extractor is code to workaround this problem, but this code is complex and difficult to maintain.
  
  The right approach, of course, should be to fix the pre-processing components directly. Unfortunately, this is tricky because we treat all pre-processing as a black box, making changes nearly impossible. 

  Pipe solves this problem by breaking up the preprocessing components. It is now easy to add your custom tokenization or sentence splitting rules. For almost any domain, we want to add a few such domain-specific rules to improve pre-processing.
  
* We have a few problems with our current schemas for NLP. 
  1. Our NLP parser outputs a file in psql-specific format that no other application can read. 
  2. When running extractors, we manually serialize and deserialize using custom logic consisting of UDFs (array_to_string) and language-specific code (String.split).
  3. Our sentences table is very wide, but most extractors only need 2 or 3 columns. This creates unnecessary I/O.
  4. Our output is lossy, because we don't store the original text (only a tokenized version), and we have lost the mapping to the original characters.
  5. It would be difficult to add coreference information to the sentences table, because it is not document-based.
  
## Schemas

With Pipe, we create a set of *minimal* schemas for the different NLP annotations. There's one schema for each type of annotation, and we currently have 18 schemas in total. The schemas are in JSON, which makes it trivial to read from and write in any programming language.

Examples:

ann.id
```
"doc123"
```

ann.text
```
"This is a very simple text file.\nIt contains two sentences."
```

ann.poss
```
["DT","VBZ","DT","RB","JJ","NN","NN",".","PRP","VBZ","CD","NNS","."]
```

ann.tokens
```
["This","is","a","very","simple","text","file",".","It","contains","two","sentences","."]
```
ann.tokenOffsets
```
[[0,4],[5,7],[8,9],[10,14],[15,21],[22,26],[27,31],[31,32],[33,35],[36,44],[45,48],[49,58],[58,59]]
```

ann.sentenceOffsets
```
[[0,32],[33,59]]
```

ann.sentenceTokenOffsets
```
[[0,8],[8,13]]
```

## Storage

We propose to store these in column format, where there exists one file for each type of schema.
Pipe contains readers and writers for column format in both [scala](src/main/scala/com/clearcut/pipe/io) and [python](../view/util/pipe.py).

For compatibility reasons, Pipe also allows you to read and write as single JSON:
```
{
  "id": "doc123",
  "text": "This is a very simple text file.\nIt contains two sentences.",
  "poss": ["DT","VBZ","DT","RB","JJ","NN","NN",".","PRP","VBZ","CD","NNS","."],
  "tokens": ["This","is","a","very","simple","text","file",".","It","contains","two","sentences","."],
 ...
}
```
And for backwards compatibility, Pipe also allows you to write in our psql-specific TSV.

## Framework

The framework allows you to plug together different preprocessing components. Currently, Pipe contains wrappers for most components of Stanford CoreNLP, as well as a components that can run an entire Stanford pipeline.

Since the components read and write our language-agnostic schemas, we can now plug together components in arbitrary programming languages including python, scala, julia.

When working with Scala, you can choose to use static typing or not. If you use static typing, [our typedefs](src/main/scala/com/clearcut/pipe/model/package.scala) make code compact and clean:
```
type ID = String
type Poss = Array[String]
type Offsets = Array[Int]
type SentenceDependencies = Array[Array[Dependency]]
type SentenceOffsets = Array[Offsets]
type SentenceTokenOffsets = Array[Offsets]
type Text = String
...
```
An example is [here](src/test/scala/BasicSpec.scala).

To build a custom tokenizer that solves the `$300. 00` problem, you can write something like 
```
import com.clearcut.pipe.annotator.Annotator
import com.clearcut.pipe.model._

class MyTokenizer extends Annotator[Text,(TokenOffsets,Tokens)] {
  override def annotate(t:(Text)):(TokenOffsets, Tokens) = {
     // add custom logic here
  }
}
```

## Tip

You can run Pipe in a regular scala REPL and manipulate your data or processing components interactively. 

You can also run our python readers and writers in a python REPL and create your own components there.

## Setup

Run `setup.sh` to install dependencies and build the parser. Pipe requires Java 8.

## Usage

Here are a few examples showing how to call Pipe with the provided launcher scripts.

```
./run.sh -i INPUT.json --formatIn json --formatOut json -v content -k doc_id -a SimpleStanfordPipeline -o OUTPUT
```
Reads INPUT.json which contains json objects with fields "doc_id" and "content". Writes results as json objects to file OUTPUT.

```
./run.sh -i INPUT.json --formatIn json --formatOut column -v content -k doc_id -a StanfordTokenizer,StanfordSentenceSplitter,StanfordPOSTagger,StanfordLemmatizer,StanfordNERTagger,StanfordSRParser -o test
```
Runs a custom set of annotators and stores results in column format.

```
/run_parallel.sh --input=INPUT.json --parallelism=10 '--formatIn json --formatOut column -v content -k doc_id -a ExtendedStanfordPipeline'
```
Splits the input file into segments and runs 10 parallel processes at a time. The ExtendedStanfordPipeline adds parse trees and true case annotations.

