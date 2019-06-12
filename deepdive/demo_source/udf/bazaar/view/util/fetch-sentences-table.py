#! /usr/bin/env python

# Legacy support for sentences table in DeepDive.
# The script reads the table from the database and stores it in the new column format.

from pyhocon import ConfigFactory
import json
import psycopg2
import psycopg2.extras
import sys
import pipe

conf = ConfigFactory.parse_file('../view.conf')

docs = conf.get('view.docs')

def find_token_offsets(s):
    # split on whitespace
    pos = [ -1 ] + [ i for i, ltr in enumerate(s) if ltr == ' ' ] + [ len(s) ]
    offsets = [ [ pos[i] + 1, pos[i + 1] ] for i in range(0, len(pos) - 1) ]
    return offsets

def write_docs():
    # write extractions to json file
    dbconf = conf.get('view.db.default')
    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (
        dbconf.get('host'),
        dbconf.get('dbname'),
        dbconf.get('user'),
        dbconf.get('password'))
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor('ann_cursor', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(docs.get('sql.query'))

    with pipe.col_open_w('../data/sentences', [ 'id', 'text', 'tokenOffsets', 'sentenceTokenOffsets', 'sentenceOffsets', 'lemmas', 'poss' ]) as w:
      sent_num = 0
      prev_document_id = None
      for row in cursor:
          # id
          #document_id = str(row[0])
          #if document_id != prev_document_id:
          #    sent_num = 0
          #id = document_id + '@' + str(sent_num)
          id = row[0]
 
          text = row[1]
          token_offsets = find_token_offsets(text)
          sentence_token_offsets = [[0,len(token_offsets)]]
          sentence_offsets = [[0, len(text)]]
          lemmas = row[2]
          pos_tags = row[3]

          w.write([id, text, token_offsets, sentence_token_offsets, sentence_offsets, lemmas, pos_tags])

          #prev_document_id = document_id
          sent_num = sent_num + 1

write_docs()

