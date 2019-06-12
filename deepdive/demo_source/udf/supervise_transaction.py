#!/usr/bin/env python
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
        p1_id="text", p1_begin="int", p1_end="int",
        p2_id="text", p2_begin="int", p2_end="int",
        doc_id="text", sentence_index="int", sentence_text="text",
        tokens="text[]", lemmas="text[]", pos_tags="text[]", ner_tags="text[]",
        dep_types="text[]", dep_token_indexes="int[]",
    ):

    # Constants
    TRANSLATION = frozenset(["转让", "交易", "卖出", "购买","收购","购入","拥有", "持有", "卖给", "买入", "获得"])
    STOCK = frozenset(["股权", "股份", "股"])
    TRANSLATION_COM = frozenset(["持股","买股","卖股"])
    TRANSLATION_AFTER = frozenset(["融资", "投资"])
    OTHERS_AFTER = frozenset(["产品", "委托", "贷款", "保险"])
    OTHERS_COM = frozenset(["购买", "提供", "申请", "销售"])
    CONF = frozenset(["对", "向"])
    OTHERS = frozenset(["销售产品", "提供担保","提供服务"])


    COMMAS = frozenset([":", "：","1","2","3","4","5","6","7","8","9","0","、", ";", "；"])
    #FAMILY = frozenset(["mother", "father", "sister", "brother", "brother-in-law"])
    MAX_DIST = 40

    # Common data objects
    p1_end_idx = min(p1_end, p2_end)
    p2_start_idx = max(p1_begin, p2_begin)
    p2_end_idx = max(p1_end,p2_end)
    intermediate_lemmas = lemmas[p1_end_idx+1:p2_start_idx]
    intermediate_ner_tags = ner_tags[p1_end_idx+1:p2_start_idx]
    tail_lemmas = lemmas[p2_end_idx+1:]
    transaction = TransactionLabel(p1_id=p1_id, p2_id=p2_id, label=None, type=None)

    # Rule: Candidates that are too far apart
    if len(intermediate_lemmas) > MAX_DIST:
        yield transaction._replace(label=-1, type='neg:far_apart')

    # Rule: Candidates that have a third company in between
    if 'ORG' in intermediate_ner_tags:
        yield transaction._replace(label=-1, type='neg:third_company_between')

    # Rule: Sentences that contain wife/husband in between
    #         (<P1>)([ A-Za-z]+)(wife|husband)([ A-Za-z]+)(<P2>)
    #if len(TRANSLATION.intersection(intermediate_lemmas)) > 0 and len(STOCK.intersection(intermediate_lemmas)) > 0:
    #    yield transaction._replace(label=1, type='A购买股权B')

    if len(TRANSLATION_COM.intersection(intermediate_lemmas)) > 0:
        yield transaction._replace(label=1, type='pos:A持股B')

    if len(TRANSLATION.intersection(intermediate_lemmas)) > 0 and len(STOCK.intersection(tail_lemmas)) > 0:
        yield transaction._replace(label=1, type='pos:A购买B股权')

    #if len(CONF.intersection(intermediate_lemmas)) > 0 and len(TRANSLATION_AFTER.intersection(tail_lemmas)) > 0:
    #    yield transaction._replace(label=1, type='pos:A向B增资')
    
    if len(TRANSLATION_AFTER.intersection(intermediate_lemmas)) > 0:
        yield transaction._replace(label=1, type='pos:A增资B')

    if len(OTHERS_COM.intersection(intermediate_lemmas)) > 0 and len(OTHERS_AFTER.intersection(tail_lemmas)) > 0:
        yield transaction._replace(label=-1, type='neg:A购买B的产品')

    if len(CONF.intersection(intermediate_lemmas)) > 0 and len(OTHERS.intersection(tail_lemmas)) > 0:
        yield transaction._replace(label=-1, type='neg:A向B提供担保')

    # Rule: Sentences that contain and ... married
    #         (<P1>)(and)?(<P2>)([ A-Za-z]+)(married)
    if ("与" in intermediate_lemmas) and ("签署股权转让协议" in tail_lemmas):
        yield transaction._replace(label=1, type='pos:A和B签署股权转让协议')
        
    if len(COMMAS.intersection(intermediate_lemmas)) > 0:
        yield transaction._replace(label=-1, type='neg:中间有特殊符号')

    #if len(CONF.intersection(intermediate_lemmas)) > 0 and len(TRANSLATION_AFTER.intersection(tail_lemmas)) > 0:
    #    yield transaction._replace(label=1, type='pos:A向B增资')

    # Rule: Sentences that contain familial relations:
    #         (<P1>)([ A-Za-z]+)(brother|stster|father|mother)([ A-Za-z]+)(<P2>)
  #  if len(FAMILY.intersection(intermediate_lemmas)) > 0:
      #  yield transaction._replace(label=-1, type='neg:familial_between')
