#! /usr/bin/env python

from os import listdir
from os.path import isfile, join
import json

# column format reader

def col_open(dir):
  return ColumnReaderAsSingleObj(dir)

def col_open_arr(dir):
  return ColumnReader(dir)

class ColumnReader(object):
  '''Reads Pipe's column format'''
  
  def __init__(self, dir):
    files = [ f for f in listdir(dir) if isfile(join(dir, f)) and not f == '.errors' ]
    self.types = [ f[f.rfind('.') + 1:] for f in files ]
    self.u_types = [ unicode(s, 'utf-8') for s in self.types ]
    self.handles = [ open(join(dir, f)) for f in files ]

  def __iter__(self):
    return self

  def next(self):
    row = [ h.readline() for h in self.handles ]
    for c in row:
      if c == '':
        self.close()
        raise StopIteration
    return [ json.loads(c.rstrip()) for c in row ]
   
  def close(self):
    for h in self.handles:
      if not h.closed:
        h.close()

class ColumnReaderAsSingleObj(ColumnReader):

  def next(self):
    row = super(self.__class__, self).next()
    obj = {}
    for i in range(0, len(row)):
      obj[self.u_types[i]] = row[i]
    return obj

# column format writer

def col_open_w(dir, types):
  return ColumnWriter(dir, types)

class ColumnWriter(object):
  '''Writes Pipe's column format'''

  def __init__(self, dir, types):
    self.types = types
    files = [ 'ann.' + t for t in types ]
    self.handles = [ open(join(dir, 'ann.' + t), 'w') for t in types ]

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    self.close()

  def write(self, arr):
    for i, a in enumerate(arr):
      self.handles[i].write(json.dumps(a) + '\n')

  def close(self):
    for h in self.handles:
      if not h.closed:
        h.close()
