#!/usr/bin/env python

from elasticsearch import Elasticsearch
import json

INPUT = "../data/sentences.json"
ES_HOST = {"host" : "localhost", "port" : 9200}
INDEX_NAME = 'dd'
TYPE_NAME = 'docs'
N = 1000

es = Elasticsearch(hosts = [ES_HOST])

es.delete_by_query(index = INDEX_NAME, body = {
      "query": {
        "match_all": {}
      }
  })

with open(INPUT, 'r') as f:
    bulk_data = []

    for line in f:
        src = json.loads(line)
        id = src['doc_id'] + '__' + src['sent_id']
        content = ' '.join(src['words'])
        op_dict = {
            "index": {
                "_index": INDEX_NAME,
                "_type": TYPE_NAME,
        	"_id": id 
            }
        }
        data_dict = {
            "id": id,
            "content": content
        }
        bulk_data.append(op_dict)
        bulk_data.append(data_dict)
        if len(bulk_data) > N:
            res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = False)
            bulk_data = [] 

if len(bulk_data) > 0:
   res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = False)

es.indices.refresh(index = INDEX_NAME)

#if es.indices.exists(INDEX_NAME):
#    res = es.indices.delete(index = INDEX_NAME)
#
#request_body = {
#    "settings" : {
#        "number_of_shards": 1,
#        "number_of_replicas": 0
#    }
#}
#
#print("creating '%s' index..." % (INDEX_NAME))
#res = es.indices.create(index = INDEX_NAME, body = request_body, ignore=400)

#print("bulk indexing...")
#res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = True)

# sanity check
#res = es.search(index = INDEX_NAME, size=2, body={"query": {"match_all": {}}})
#print(" response: '%s'" % (res))

#print("results:")
#for hit in res['hits']['hits']:
#    print(hit["_source"])

