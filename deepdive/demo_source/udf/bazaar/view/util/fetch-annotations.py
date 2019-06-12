#!/usr/bin/env python

from pyhocon import ConfigFactory
import json
import psycopg2
import psycopg2.extras
import sys

conf = ConfigFactory.parse_file('../view.conf')

conf_annotations = conf.get_list('view.annotations')

def write_annotations():
    # write extractions to json file
    dbconf = conf.get('view.db.default')
    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (
        dbconf.get('host'),
        dbconf.get('dbname'),
        dbconf.get('user'),
        dbconf.get('password'))
    conn = psycopg2.connect(conn_string)
    for ann in conf_annotations:
      with open('../' + ann.get('input'), 'w') as w:
        cursor = conn.cursor('ann_cursor', cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(ann.get('sql.query'))
        for row in cursor:
            #print(row)
            # TODO: must write into the following format
            # each row:
            # {"range":{"type":"sentenceTokenSpan","doc_id":"doc123","sentNum":0,"f":3,"t":4},"target":{"entity":"something"}}
            # save in file using w.write
            obj = {"id":row[0], "range":{"type":"sentenceTokenSpan","doc_id":row[1],"sentNum":0,"f":row[2],"t":int(row[3])},"target":{"entity":row[4]}}
            w.write(json.dumps(obj))
            w.write('\n')

write_annotations()
