#!/usr/bin/env python3
#encoding:utf-8
from deepdive import *
import random
from collections import namedtuple

TransactionLabel = namedtuple('TransactionLabel', 'p1_id, p2_id, label, type')

@tsv_extractor
@returns(lambda
        p1_id   = "text",
        p2_id   = "text",
        label   = "int",
        rule_id = "text",
    :[])
# heuristic rules for finding positive/negative examples of transaction relationship mentions
def supervise(
        p1_id="text", p1_name="text",p1_begin="int", p1_end="int",
        p2_id="text", p2_name="text",p2_begin="int", p2_end="int",
        doc_id="text", sentence_index="int", sentence_text="text",
        tokens="text[]", lemmas="text[]", pos_tags="text[]", ner_tags="text[]",
        dep_types="text[]", dep_token_indexes="int[]",
    ):

   
    # Common data objects
    if p1_begin!=min(p1_begin, p2_begin):
        p1_begin,p2_begin = p2_begin,p1_begin
        p1_end,p2_end = p2_end,p1_end
        p1_name,p2_name = p2_name,p1_name
        
    intermediate_lemmas = lemmas[p1_end+1:p2_begin]
    intermediate_ner_tags = ner_tags[p1_end+1:p2_begin]
    tail_lemmas = lemmas[p2_begin+1:]
    transaction = TransactionLabel(p1_id=p1_id, p2_id=p2_id, label=None, type=None)
    
    
    if "中国证券登记结算有限责任公司" in p1_name or "中国证券登记结算有限责任公司" in p2_name:
        yield transaction._replace(label=-2, type='A 或 B 是 中国证券登记结算有限责任公司 ')
        
        
    if "人民法院" in p2_name or "人民法院" in p1_name:
        yield transaction._replace(label=-2, type='A 或 B 是 人民法院 ') 
       
    if  "B-Ni"not in intermediate_ner_tags and  all(x in intermediate_lemmas for x in ["质押","给"]):
        yield transaction._replace(label=1, type='A 质押给 B')

    if  "B-Ni"not in intermediate_ner_tags and  all(x in intermediate_lemmas for x in ["质押人","为"]):
        yield transaction._replace(label=1, type='A 做了质押，质押人为: B')
    
    if "B-Ni" in intermediate_ner_tags and all(x in intermediate_lemmas for x in ["分别","质押"]):
        yield transaction._replace(label=1, type='A 分别质押给B，C,D，，，')
    
    if all(x in intermediate_lemmas for x in ["在","中国","证券","登记","结算","有限","责任","公司","办理"]) and "质押" in tail_lemmas:
        yield transaction._replace(label=1, type='A 在中国证券登记结算有限责任公司办理了与B 的质押的解除手续')
    
    if (any(x in intermediate_lemmas for x in ["接到","收到"]) and "股东" in intermediate_lemmas) and any(x in lemmas[p2_end+1] for x in ["函告","通知","出具"]):
        yield transaction._replace(label=-1, type='A 接到/收到 股东 B 通知/函告/出具')     
    
    if "向" in intermediate_lemmas and all(x in tail_lemmas for x in ["申请","质押"]):
        yield transaction._replace(label=1, type='A向B申请质押贷款')
    
