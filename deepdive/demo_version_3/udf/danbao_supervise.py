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
		
	head_lemmas = lemmas[:p1_begin]
	intermediate_lemmas = lemmas[p1_end+1:p2_begin]
	intermediate_ner_tags = ner_tags[p1_end+1:p2_begin]
	tail_lemmas = lemmas[p2_begin+1:]
	transaction = TransactionLabel(p1_id=p1_id, p2_id=p2_id, label=None, type=None)


	if any((x in intermediate_lemmas) for x in ["为"]) and any((x in tail_lemmas for x in ["提供", "担保", "反担保"])):
		yield transaction._replace(label=1, type='A 为 B 提供担保')
	
	if any((x in intermediate_lemmas) for x in ["由"]) and any((x in tail_lemmas for x in ["提供", "担保"])):
		yield transaction._replace(p1_id=p2_id, p2_id=p1_id, label=1, type='A 由 B提供担保 \ B 为 A提供担保')

	if "银行" in p1_name or "银行" in p2_name or p1_name.endswith("支行") or p2_name.endswith("支行"):
		yield transaction._replace(label=-2, type='A 或 B是银行')
	
	if "担保人" in head_lemmas and "被担保人" in intermediate_lemmas:
		yield transaction._replace(label=1, type='A 为 B 担保')
	
	if "互保" in tail_lemmas:
		yield transaction._replace(label=1, type="A 为 B 担保")
		yield transaction._replace(p1_id=p2_id, p2_id=p1_id, label=1, type="B 为 A 担保")
	
	if all((x not in intermediate_lemmas) for x in ["为", "给", "由"]) or any((x in intermediate_lemmas) for x in ["和", "与", "及"]) and "B-Ni" not in intermediate_ner_tags:
		yield transaction._replace(label=-1, type="A 与 B")
