#!/usr/bin/env python

from elasticsearch import Elasticsearch
import json

EXTRACTOR='genepheno'
INPUT='../data/genepheno_rel.json'
ES_HOST = {"host" : "localhost", "port" : 9200}
INDEX_NAME = 'dd'
TYPE_NAME = 'docs'
N = 1000

es = Elasticsearch(hosts = [ES_HOST])

with open(INPUT, 'r') as f:
    bulk_data = []

    for line in f:
        src = json.loads(line)
        id = src['doc_id'] + '__' + str(src['sent_id'])
        op_dict = {
            "update": {
                "_index": INDEX_NAME,
                "_type": TYPE_NAME,
        	"_id": str(id) 
            }
        }
        extr = ','.join(map(str, src['gene_wordidxs'])) + '-' + ','.join(map(str, src['pheno_wordidxs']))
        script_dict = {
            "script" : "if (ctx._source.containsKey(\"" + EXTRACTOR + "\")) {ctx._source[\"" + EXTRACTOR + "\"] += ex;} else {ctx._source[\"" + EXTRACTOR + "\"] = [ex]}",
            "params" : {
                "ex" : extr
            }
        }
        bulk_data.append(op_dict)
        bulk_data.append(script_dict)
        if len(bulk_data) > N:
            res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = False)
            bulk_data = [] 

if len(bulk_data) > 0:
   print('doing update')
   res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = False)

es.indices.refresh(index = INDEX_NAME)

