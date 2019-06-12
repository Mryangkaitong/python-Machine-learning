#!/usr/bin/env python

# Author: Zifei Shan (zifeishan@gmail.com)

''' This file construct a sentence table from ann.* files generated from Pipe project.

Example usage:

    python generate_sentence_table.py  DIRECTORY/OF/ANN/  > output_sentences.tsv

The generated sentence table follow the format below:

    CREATE TABLE sentences (
     doc_id       text,
     sent_id      integer,
     wordidxs     integer[],
     words        text[],
     poses        text[],
     ners         text[],
     lemmas       text[],
     dep_tuples   text[],  -- Triplet format. e.g.: "1 dep 0"
     sentence_id  text
    );

'''

import sys, json

# This file can accept an argument: the folder that contains ann.*
# If not specified, use the current directory.
if len(sys.argv) == 1:
  basedir = ''  
else:
  basedir = sys.argv[1] + '/'

# Helper functions

def list2TSVarray(a_list, quote=True):
  '''Convert a list to a string that can be used in a TSV column and intepreted as
  an array by the PostreSQL COPY FROM command.
  If 'quote' is True, then double quote the string representation of the
  elements of the list, and escape double quotes and backslashes.
  '''
  if a_list is None:
    return '\\N'

  if quote:
    for index in range(len(a_list)):
      if "\\" in unicode(a_list[index]):
        # Replace '\' with '\\\\"' to be accepted by COPY FROM
        a_list[index] = unicode(a_list[index]).replace("\\", "\\\\\\\\")
      # This must happen the previous substitution
      if "\"" in unicode(a_list[index]):
        # Replace '"' with '\\"' to be accepted by COPY FROM
        a_list[index] = unicode(a_list[index]).replace("\"", "\\\\\"")
    string = ",".join(list(map(lambda x: "\"" + unicode(x) + "\"", a_list)))
  else:
    string = ",".join(list(map(lambda x: unicode(x), a_list)))
  return "{" + string + "}"

def open_file(fname):
  '''
  Opens a file, if not found, return None.
  '''
  try:
    return open(fname)
  except:
    return None

def read_js_line(fp):
  '''
  Return None if file is not open. Otherwise read a line from file.
  If '' returned, EOF is found.
  '''
  if fp == None:
    return None
  s = fp.readline()
  if s == '':
    return ''
  else:
    return json.loads(s)

def escape_none(s):
  '''
  Just escaping a None into psql-friendly format
  '''
  if s is None:
    return '\\N'
  return unicode(s).encode('utf-8')

def findTokenOffset(token_offsets, sent_offset):
  '''
  Construct sent_token_offsets
  '''
  start = min(i for i in range(len(token_offsets)) if token_offsets[i][0] == sent_offset[0]) 
  end = max(i for i in range(len(token_offsets)) if token_offsets[i][1] == sent_offset[1]) + 1
  return start, end

# ----------- Main function -------------

# Assume fixed filenames
fdoc_id = open_file(basedir + 'ann.id')
flemma = open_file(basedir + 'ann.lemmas')
fpos = open_file(basedir + 'ann.poss')
fner = open_file(basedir + 'ann.nerTags')
fsent_offset = open_file(basedir + 'ann.sentenceOffsets')
fsent_token_offset = open_file(basedir + 'ann.sentenceTokenOffsets')
ftext = open_file(basedir + 'ann.text')
ftoken_offset = open_file(basedir + 'ann.tokenOffsets')
fsent_deps = open_file(basedir + 'ann.sentenceDependencies')

while True:
  doc_id = read_js_line(fdoc_id)
  lemmas = read_js_line(flemma)
  poss = read_js_line(fpos)
  ners = read_js_line(fner)
  sent_offsets = read_js_line(fsent_offset)
  # sent_token_offsets = read_js_line(fsent_token_offset)
  text = read_js_line(ftext)
  token_offsets = read_js_line(ftoken_offset)
  sent_deps = read_js_line(fsent_deps)

  if any(x == '' for x in [doc_id, lemmas, poss, sent_offsets, \
    text, token_offsets]):
    break

  sent_token_offsets = [ findTokenOffset(token_offsets, x) for x in sent_offsets]

  # loop through each sentence
  sent_words = [text[o[0] : o[1]] for o in token_offsets]
  # print 'WORDS:', sent_words


  for sent_id in range(len(sent_token_offsets)):
    sent_from, sent_to = sent_token_offsets[sent_id]
    sentence_id = unicode(doc_id) + '_' + unicode(sent_id)
    if sent_deps is not None:
      # e.g.: [[{"name":"det","from":1,"to":0}],[{"name":"advmod","from":1,"to":0},{"name":"advmod","from":1,"to":2}]]
      this_sent_deps = ['%d %s %d' % (d['from'], d['name'], d['to']) for d in sent_deps[sent_id]]
    print '\t'.join([escape_none(x) for x in [ \
      doc_id, \
      sent_id, \
      list2TSVarray([x for x in range(sent_to - sent_from)]), \
      list2TSVarray( sent_words[ sent_from : sent_to] ) if sent_words is not None else None, \
      list2TSVarray( poss[ sent_from : sent_to]) if poss is not None else None, \
      list2TSVarray( ners[ sent_from : sent_to]) if ners is not None else None, \
      list2TSVarray( lemmas[ sent_from : sent_to]) if lemmas is not None else None, \
      list2TSVarray( this_sent_deps ) if sent_deps is not None else None, \
      sentence_id \
    ]])
