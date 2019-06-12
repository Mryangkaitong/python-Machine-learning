#!/usr/bin/env bash

#curl -XGET 'http://localhost:9200/view/docs/_search?q=_id:10.1371.journal.pone.0042439.Body__50'
curl -XGET 'http://localhost:9200/view/docs/_search?q=_id:doc123'
curl -XGET 'http://localhost:9200/view/docs/_search?q=simple'
