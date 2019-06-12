#!/usr/bin/env python

import pipe

ES_HOST = {"host" : "localhost", "port" : 9200}
INDEX_NAME = 'view'
TYPE_NAME = 'docs'
N = 1000

from pyhocon import ConfigFactory
from elasticsearch import Elasticsearch
import json
import sys

conf = ConfigFactory.parse_file('../view.conf')

docs_conf = conf.get('view.docs')

es = Elasticsearch(hosts = [ES_HOST])

def index_docs():

    # clear index
    es.delete_by_query(index = INDEX_NAME, doc_type = TYPE_NAME, body = {
        "query": {
          "match_all": {}
        }
    })

    # bulk index docs
    bulk_data = []
    for o in pipe.col_open('../' + docs_conf.get('input')):
        id = o[u'id']
        content = o[u'text']
        tokenOffsets = o[u'tokenOffsets']

        op_dict = {
            "index": {
                "_index": INDEX_NAME,
                "_type": TYPE_NAME,
                "_id": id
            }
        }
        #data_dict = {
        #    "id": id,
        #    "content": content,
        #    "tokenOffsets": tokenOffsets
        #}
        o['content'] = o[u'text']
        data_dict = o
        bulk_data.append(op_dict)
        bulk_data.append(data_dict)
        if len(bulk_data) > N:
            res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = False)
            bulk_data = []

    if len(bulk_data) > 0:
        res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = False)

    es.indices.refresh(index = INDEX_NAME)

index_docs()
