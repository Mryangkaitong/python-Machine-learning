#!/usr/bin/env bash

# exists
HEAD=$(curl -s -XHEAD -i 'http://localhost:9200/view')
[ "${HEAD:0:15}" == "HTTP/1.1 200 OK" ] && EXISTS=1
if [ $EXISTS ]; then
  curl -XDELETE 'http://localhost:9200/view/'
fi

INDEX_NAME=view
TYPE_DOCS_NAME=docs

curl -XPOST localhost:9200/$INDEX_NAME -d '{
  "settings" : {
    "index" : {
      "number_of_shards" : 1
    },
    "analysis" : {
      "analyzer" : {
        "fulltext_analyzer" : {
          "type" : "custom",
          "tokenizer" : "whitespace",
          "filter" : [
            "lowercase"
          ]
        }
      }
    }
  },
  "mappings" : {
    "annotations" : {
      "_source" : { "enabled" : true },
      "_parent" : {
          "type" : "docs"
       },
      "properties" : {}
    },
    "docs" : {
      "_source" : { "enabled" : true },
      "properties" : {
          "id" : {
            "type" : "string"
          },
          "content" : { 
            "type" : "string", 
            "term_vector" : "with_positions_offsets",
            "store" : false,
            "index_analyzer" : "fulltext_analyzer",
            "norms" : {
               "enabled" : false
            }
          },
          "text" : {
            "type" : "string",
            "term_vector" : "with_positions_offsets",
            "index_analyzer" : "fulltext_analyzer"
          },
          "extr1" : {
            "type" : "string",
            "index" : "not_analyzed"
          },
          "extr1_meta" : {
            "type" : "string",
            "index" : "not_analyzed"
          }
        }
      }
    }
  }'
