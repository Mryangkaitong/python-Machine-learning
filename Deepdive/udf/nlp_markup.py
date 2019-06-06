#!/usr/bin/env python
#encoding:utf-8
from deepdive import *
from transform import *

@tsv_extractor
@returns(lambda
        doc_id         = "text",
        sentence_index = "int",
        sentence_text  = "text",
        tokens         = "text[]",
        lemmas         = "text[]",
        pos_tags       = "text[]",
        ner_tags       = "text[]",
        dep_types      = "text[]",
        dep_tokens     = "int[]",
    :[])
def extract(
        sentences_list  = "text",
    ):
    """
    使用pyltp 提取文本信息
    """
    sentences_list = sentences_list.split("&&&&")
    doc_id = sentences_list[0]
    sentence_index = int(sentences_list[1])
    sentence_text = sentences_list[2]
    tokens = sentences_list[3].split("@@")
    lemmas = tokens
    pos_tags = sentences_list[4].split("@@")
    ner_tags = sentences_list[5].split("@@")
    dep_types = sentences_list[6].split("@@")
    dep_tokens = list(map(lambda x:int(x),sentences_list[7].split("@@")))
    yield [
        doc_id,
        sentence_index,
        sentence_text,
        tokens,
        lemmas,
        pos_tags,
        ner_tags,
        dep_types,
        dep_tokens,
        ]
