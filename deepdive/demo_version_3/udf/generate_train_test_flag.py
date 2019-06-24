#!/usr/bin/env python3
#encoding:utf-8
from deepdive import *
from transform import *
import random

@tsv_extractor
@returns(lambda
        p1_id           = "text",
        p2_id           = "text",
        vote_sum        = "int",
        test_train_flag = "int",
    :[])
def extract(
        p1_id           = "text",
        p2_id           = "text",
        vote_sum        = "int",
    ):
    p1_id_cur = p1_id
    p2_id_cur = p2_id
    vote_sum_cur = vote_sum
    test_train_flag = random.randint(1,10)
    yield [
        p1_id_cur,
        p2_id_cur,
        vote_sum_cur,
        test_train_flag,
    ]
