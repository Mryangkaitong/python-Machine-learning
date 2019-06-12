import java.io.{BufferedWriter, OutputStreamWriter, FileOutputStream}
import java.util.Properties
import javax.swing.text.html.parser.DocumentParser

import com.clearcut.pipe.annotator._
import com.clearcut.pipe.{Schema, Main}
import com.clearcut.pipe.io.{ColumnWriter, ColumnReader, Json}
import com.clearcut.pipe.model.Text
import org.scalatest.{Matchers, FlatSpec}

/**
 *
 * Note: SRParser needs a lot of memory. You have to run the test like this:
 * sbt -mem 4096 test
 *
 */
class BasicSpec extends FlatSpec with Matchers {

  def createTextFile(dir:String) = {
    val w = new BufferedWriter(new OutputStreamWriter
      (new FileOutputStream(dir + "/ann.text")))
    w.write(Json.write("This is a very simple text file.\nIt contains two sentences."))
    w.close
  }

  "ColumnReader and ColumnWriter" should "work" in {
    import java.nio.file.{Path, Paths, Files}
    val folderPath: Path = Paths.get(System.getProperty("java.io.tmpdir"))
    var dir: Path = Files.createTempDirectory(folderPath, "pipe")

    println(dir.toString)

    createTextFile(dir.toString)

    val annotators:Array[Annotator[_,_]] = Array(
      new StanfordTokenizer,
      new StanfordSentenceSplitter,
      new StanfordPOSTagger
      //new StanfordLemmatizer
    )

    val r = new ColumnReader(dir.toString)
    val w = new ColumnWriter(dir.toString)
    val e = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(dir + "/.errors")))

    Main.run(annotators, r, w, e)

    r.close
    w.close
    e.close
  }


}
