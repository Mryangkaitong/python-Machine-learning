#!/usr/bin/python
# coding=utf-8
#Function:
#	match mention and entity
#Data:
#	2016-3-16

import re

MAX_LEN = 50

def link(str, dict):
    str, flag = removeFx(str)
    # remove the mention that is too long
    if len(str) > 50:
        return None
    # remove the mention has symbol other than chinese
    p = r'\d+'
    m = re.findall(p, str)
    if m != []:
        return None
    # remove the mention has word that implies not a comp mention
    negativeword = ['交易所', '证监会', '银行', '监督', '管理', '委员会', '国务院','保监会', '政府', '酒店', '财政局', '事务所', '商务部', '发改委', '证券报']
    for word in negativeword:
        if str.find(word) >= 0:
            return None
        
    entity = match(str, dict)
    if entity == None:
        if flag == False:
            return None
        else:
            return str
    else:
        return entity
        
# remove the common prefix and suffix
def removeFx(str):
	flag = False
	dict1 = ['(', ')', '（', '）']
	dict2 = ['股份', '有限', '公司', '集团', '投资']
	comp = ['总公司','公司','有限','集团','股份','投资','发展','责任','合伙','销售','合作']
	symbol = ['(',')','《','》','（','）']
	for word in symbol:
		str = str.replace(word, '')
	for word in comp:
		str = str.replace(word, '')
		flag = True
	return str, flag

def loaddict(filename):
	dict = []
	file = open(filename, 'r')
	for line in file.readlines():
		line = line.strip('\n')
		dict.append(line)
	return dict

def match(mention, entity_dict):
	'''
	testing if a mention is an entity
	'''
	for entity in entity_dict:
		res = entity_match(mention, entity)
		if res != None:
			return res	
	return None

def entity_match(mention, entity):
	'''
	testing if a mention matchs a entity
	'''
	if mention.find(entity) >= 0:
		return entity
	else:
		return None

if __name__ == '__main__':
	dict = loaddict("../input/company.csv")
	mention = "平安银行"
	res = match(mention, dict)
