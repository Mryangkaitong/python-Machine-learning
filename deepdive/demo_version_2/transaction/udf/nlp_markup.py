#!/usr/bin/env python3
#encoding:utf-8
from deepdive import *
from transform import *
import pyltp
import numpy as np
import os
import sys
#加载ltp相关模型
LTP_DIR = "/root/transaction/udf/model/ltp_data_v3.4.0"

#分词模型
segmentor = pyltp.Segmentor()
segmentor.load(os.path.join(LTP_DIR, "cws.model"))

#词性模型
postagger = pyltp.Postagger()
postagger.load(os.path.join(LTP_DIR, 'pos.model'))

#命名实体模型
recognizer = pyltp.NamedEntityRecognizer()
recognizer.load(os.path.join(LTP_DIR, 'ner.model'))

#依存句法分析
parser = pyltp.Parser() 
parser.load(os.path.join(LTP_DIR, 'parser.model'))  



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
        doc_id  = "text",
        content  = "text",
    ):
    """
    使用pyltp 提取文本信息
    """
    #分句
    sents = pyltp.SentenceSplitter.split(content)
    #     token_offset = 0
    for index,sent in enumerate(list(sents)):
        #doc_id:文章id
        doc_id = doc_id
        #sentence_index:句子id
        sentence_index = index+1
        #sentence_text
        sentence_text = sent
        #tokens：分词
        tokens = list(segmentor.segment(sent))  
        #lemmas：词元
        lemmas = tokens
        #pos_tags:词性
        pos_tags = list(postagger.postag(tokens))
        #ner_tags:命名实体
        ner_tags = list(recognizer.recognize(tokens, pos_tags))
#         #doc_offsets:单词偏移量
#         token_length = list(map(lambda x:len(x),tokens))
#         token_length.insert(0, token_offset)
#         token_length = np.array(token_length)
#         doc_offset = token_length.cumsum(0)
#         sentence.append(list(doc_offset[:-1]))
#         token_offset = doc_offset[-1]

        #dep_types，dep_tokens：依存句法
        arcs = parser.parse(tokens, pos_tags)
        arcs = np.array(list(map(lambda x: [x.head,x.relation],arcs)))
        dep_types = map(lambda x: str(x),list(arcs[:,1]))
       # print(dep_types,file=sys.stderr)
        #print(type(dep_types),file=sys.stderr)
        dep_tokens = map(lambda x:int(x),list(arcs[:,0]))
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
