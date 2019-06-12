#!/usr/bin/env python
#encoding:utf-8
from deepdive import *
from transform import *
import re

@tsv_extractor
@returns(lambda
        mention_id       = "text",
        mention_text     = "text",
        doc_id           = "text",
        sentence_index   = "int",
        begin_index      = "int",
        end_index        = "int",
    :[])
def extract(
        doc_id         = "text",
        sentence_index = "int",
        tokens         = "text[]",
        ner_tags       = "text[]",
    ):
    """
    Finds phrases that are continuous words tagged with ORG.
    """
    num_tokens = len(ner_tags)
    # find all first indexes of series of tokens tagged as ORG
    first_indexes = (i for i in xrange(num_tokens) if ner_tags[i] == "ORG" and (i == 0 or ner_tags[i-1] != "ORG") and re.match(u'^[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ffa-zA-Z]+$', unicode(tokens[i], "utf-8")) != None)
    for begin_index in first_indexes:
        # find the end of the ORG phrase (consecutive tokens tagged as ORG)
        end_index = begin_index + 1
        while end_index < num_tokens and ner_tags[end_index] == "ORG" and re.match(u'^[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ffa-zA-Z]+$', unicode(tokens[end_index], "utf-8")) != None:
            end_index += 1
        end_index -= 1
        # generate a mention identifier
        mention_id = "%s_%d_%d_%d" % (doc_id, sentence_index, begin_index, end_index)
        mention_text = "".join(map(lambda i: tokens[i], xrange(begin_index, end_index + 1)))
        temp_text = link(mention_text, entity_dict)
        if temp_text == None or temp_text == '':
            continue
        if end_index - begin_index >= 25:
            continue
        # Output a tuple for each ORG phrase
        yield [
            mention_id,
            mention_text,
            doc_id,
            sentence_index,
            begin_index,
            end_index,
        ]
