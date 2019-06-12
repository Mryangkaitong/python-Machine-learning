#!/usr/bin/env python

ES_HOST = {"host" : "localhost", "port" : 9200}
INDEX_NAME = 'view'
TYPE_ANNOTATORS_NAME = 'annotators'
TYPE_ANNOTATIONS_NAME = 'annotations'
N = 1000

from pyhocon import ConfigFactory
from elasticsearch import Elasticsearch
import json
import sys

conf = ConfigFactory.parse_file('../view.conf')

conf_annotations = conf.get_list('view.annotations')

es = Elasticsearch(hosts = [ES_HOST])

# create a small table that only contains the names of all available extractors
def index_annotators():
  es.delete_by_query(index = INDEX_NAME, doc_type = TYPE_ANNOTATORS_NAME, body = {
      "query": {
        "match_all": {}
      }
  })
  for ann in conf_annotations:
    es.index(index = INDEX_NAME, doc_type = TYPE_ANNOTATORS_NAME, body = {
      "name" : ann.get('name')
    }, refresh = False)
  es.indices.refresh(index = INDEX_NAME)

# create a large table that contains all extractions
def index_annotations():
  es.delete_by_query(index = INDEX_NAME, doc_type = TYPE_ANNOTATIONS_NAME, body = {
      "query": {
        "match_all": {}
      }
  })
  for ann in conf_annotations:
    # read from file

    # bulk index docs
    bulk_data = []
    for l in open('../' + ann.get('input')):
        o = json.loads(l)
        # {"id": "12", "range":{"type":"sentenceTokenSpan","doc_id":"doc123","sentNum":0,"f":3,"t":4},"target":{"entity":"something"}}
        o['attribute'] = ann.get('name')
        op_dict = {
            "index": {
                "_index": INDEX_NAME,
                "_type": TYPE_ANNOTATIONS_NAME,
                "_id": o['id'],
                "_parent": o['range']['doc_id']
            }
        }
        #data_dict = {
        #    "id": id,
        #    "content": content,
        #    "tokenOffsets": tokenOffsets
        #}
        #o['content'] = o[u'text']
        data_dict = o
        #print(op_dict)
        #print(data_dict)
        bulk_data.append(op_dict)
        bulk_data.append(data_dict)
        if len(bulk_data) > N:
            res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = False)
            bulk_data = []

    if len(bulk_data) > 0:
        res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = False)

    es.indices.refresh(index = INDEX_NAME)

index_annotators()
index_annotations()

