Parser
======

Run `setup.sh` to install dependencies and build the parser.

We assume that your input has the following format. There's one line per document and each document is a JSON object with a key and content field.

```json
{ "item_id":"doc1", "content":"Here is the content of my document.\nAnd here's another line." }
{ "item_id":"doc2", "content":"Here's another document." }
```

You can run the NLP pipeline on 1 core as follows:

```bash
cat input.json | ./run.sh -i json -k "item_id" -v "content" > output.tsv
```

You can run the NLP pipeline on 16 cores as follows:
```bash
./run_parallel.sh -in="input.json" --parallelism=16 -i json -k "item_id" -v "content"
```

You can run the NLP pipeline as a REST service as follows:

```bash
./run.sh -p 8080
```

The output will be files in tsv-format that you can directly load into the database.


## Setup

This package requires Java 8. 

