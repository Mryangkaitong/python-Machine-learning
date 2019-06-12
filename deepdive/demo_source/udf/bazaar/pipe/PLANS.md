
Plans
=====

Change annotator schema to something like

```
class Annotator[A,B] {}

class StanfordTokenizer[C <: HasText, D <: HasTokens with HasTokenOffsets] extends Annotator[C,D] {}
```

Then the readers can be type-safe, too:

```
val r = new ColumnReader[HasText with HasID]
```

Internally, the reader can look for the right files.

And to build a concrete object:

```
trait HasInt { def getInt:Int }
trait HasString { def getString:String }

val obj:HasInt with HasString =
   new HasInt with HasString {
     def getInt = 12
     def getString = "hello"
   }
```

Open question: how to merge two objects?

If we do multiple extractions, and then want to merge the results:

val obj1:HasX with HasY
val obj2:HasZ

val obj = ????

