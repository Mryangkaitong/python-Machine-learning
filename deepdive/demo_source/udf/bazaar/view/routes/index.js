var express = require('express');
var router = express.Router();
var path = require('path');

var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({
  host: 'http://localhost:9200'
});

router.get('/', function(req, res, next) {
  //res.render('index', { title: 'Express3' });
  res.sendFile(path.join(__dirname + '/../public/index.html'));
});

router.get('/search*', function(req, res, ext) {
  //res.render('index', { title: 'Express3' });
  res.sendFile(path.join(__dirname + '/../public/index.html'));
});

router.get('/annotators', function(req, res, next) {
  var index = req.query.index || 'view'
  client.search({
    index: index, //process.env.INDEX_NAME,
    type: 'annotators',
    body: {
      query: {
        'match_all': {}
      }
    }
  }).then(function(body) {
    var hits = body.hits.hits;
    res.send(hits);
  }, function (err) {
    console.trace(err.message);
    next(err);
  });
});

router.get('/annotations', function(req, res, next) {
  var doc_ids = []
  var doc_ids_str = req.param('doc_ids')
  if (doc_ids_str) doc_ids = doc_ids_str.split(',') 
  var index = req.query.index || 'view'

  var obj = {
    index: index, //process.env.INDEX_NAME,
    type: 'annotations',
    from: 0,
    size: 100000,
    body: {
      "query" : {
        "has_parent": {
          "type": "docs", 
          "query": {
            "ids" : {
              "values" : doc_ids
            }
          }
        }
      }
    }
  }

  client.search(
   obj
  ).then(function (body) {
    var hits = body.hits.hits;
    res.send(hits)
  }, function (err) {
    console.trace(err.message);
    next(err)
  });
});



router.get('/docs', function(req, res, next) {
  var from = req.param('from', 0)
  var limit = req.param('limit', 100)
  var keywords = req.query.keywords || ''
  var facets = req.query.facets || ''
  var index = req.query.index || 'view'

  var obj = {
    index: index, //process.env.INDEX_NAME,
    type: 'docs',
    from: from,
    size: limit,
    body: {
      query: {
        "match_all" : {}
      },
      highlight : {
        fields : {
          content : { "number_of_fragments" : 0 }
        }
      }
    }
  }

  if (keywords.length > 0) {
    obj.body.query = {
        query_string: {
          "default_field" : "content",
          "fields" : ["content", "_id", "id"],
          "query" : keywords
        }
      }
  }

  if (facets.length > 0) {
    var l = facets.split(',')

    var filters = []
    for (var i=0; i < l.length; i++)
      filters.push({
        //"exists" : { "field" : l[i] }
        "has_child" : {
           "type" : "annotations",
           "query" : {
              "term" : {
                "attribute" : l[i]
              }
           }
        }
      });

    if (filters.length > 1)
      obj.body.filter = {
        "and" : filters
      }
    else
      obj.body.filter = filters[0]
  }

  client.search(obj).then(function (body) {
    var docs_context = body.hits
    var docs = body.hits.hits;
   
    // we now have the documents, run another query to get all annotations on
    // these documents 
    var doc_ids = new Array(docs.length)
    for (var i=0, ii = docs.length; i < ii; i++)
      doc_ids[i] = docs[i]._id

    var obj = {
      index: index, //process.env.INDEX_NAME,
      type: 'annotations',
      from:0,
      size:100000,
      body: {
        "query" : {
          "has_parent": {
            "type": "docs",
            "query": {
              "ids" : {
                "values" : doc_ids
              }
            }
          }
        }
      }
    }
    client.search(obj).then(function(body) {
      var hits = body.hits.hits
      // build a little index of the annotations
      var id2ann = {}
      for (var i = 0, ii = hits.length; i < ii; i++) {
        var id = hits[i]._source.range.doc_id
        if (id in id2ann)
          id2ann[id].push(hits[i]._source)
        else
          id2ann[id] = [hits[i]._source]
      }
      // add to docs
      for (var i=0, ii = docs.length; i < ii; i++) {
        docs[i].annotations = id2ann[docs[i]._id] || []
      } 
      res.send(docs_context) 
    }, function(err) {
      console.trace(err.message);
      next(err)
    });
    
    //res.send(hits)

  }, function (err) {
    console.trace(err.message);
    next(err)
  });
});


module.exports = router;
