#!/usr/bin/env python

from elasticsearch import Elasticsearch
import json

ES_HOST = {"host" : "localhost", "port" : 9200}
INDEX_NAME = 'dd'
TYPE_NAME = 'extractors'

es = Elasticsearch(hosts = [ES_HOST])

es.delete_by_query(index = INDEX_NAME, doc_type = TYPE_NAME, body = {
      "query": {
        "match_all": {}
      }
})


es.index(index = INDEX_NAME, doc_type = TYPE_NAME, body = {
  "name" : "genepheno"
}, refresh = False)

es.indices.refresh(index = INDEX_NAME)

