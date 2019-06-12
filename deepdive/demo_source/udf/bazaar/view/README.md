View
====

View visualizations of extractions and NLP annotations. Search by keywords.


## Installation

Run `./setup.sh` to install dependencies.

Make sure you run `source env.sh` each time you run view.

You can use `./run.sh` to run the two servers (elasticsearch and nodejs). 

## How to index your data

* To update view's index, adjust `view.conf` and run tools in `./util`.

* The documents should be in [Pipe](../pipe)'s column format. We have included the tool `./fetch-sentences-table.py` which dumps the sentences table from DeepDive and converts it into column format. This tool has been tested with DeepDive's spouse example, so it assumes that the sentences table has a that schema. 

* Then fetch extractor output by running `./fetch-anntations.py`. This tool dumps a candidate or inference table from DeepDive and converts it into the right format.

* Create the elasticsearch indexes by running:

  ```
  ./create_index.sh
  ./refresh-documents.py
  ./refresh-annotations.py
  ``` 

* Visit `http://localhost:3000`.

View actually uses two elasticsearch indexes: one containing all documents and their NLP annotations, the other containing all extractions. Typically, the documents index is very large and the extractions index relatively small. By separating the two it is now possible to update the extractions index extremely quickly. This is great for extractor development, since an update to an extractor doesn't require rebuilding the documents index. On the spouse example, updating the extractions index now takes only about 5 seconds.

To make sure that retrieval of documents and their extractions remains very fast, the two indexes are linked through elasticsearch'es Parent-Child mapping. Each document (parent) has a mapping to a set of extractions (children). This mapping is represented as a hashmap over IDs and is cached in memory while elasticsearch is running.  

