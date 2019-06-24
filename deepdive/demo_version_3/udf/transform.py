#!/usr/bin/python3
#coding=utf-8
#Program:
#	transform the full name in pos* files into short name
#Date:
#	2016-3-16

from entity_match import *

ENTITY_FILE = "/root/transaction/udf/company_full_short.csv"
entity_dict = loaddict(ENTITY_FILE)

def loaddict(filename):
	dict = {}
	file = open(filename, "r")
	file.readline()
	for line in file.readlines():
		coms = line.split()
		full = coms[0]
		short = coms[1]
		dict[full] = short
	return dict

def transformFile(filename, dict):
	comp = ['总公司','公司','有限','集团','股份','投资','发展','责任','合伙','销售','合作']
	symbol = ['(',')','《','》','（','）']
	fin = open(filename, "r")
	#fout = open(filename.split('.')[0] + ".out.csv", "w")
	for line in fin.readlines():
		coms = line.split(",")
		com1 = coms[0]
		com2 = coms[1]
		
		#for word in comp:
		#    com1 = com1.replace(word, '');
		#    com2 = com2.replace(word, '');
		#for word in symbol:
		#    com1 = com1.replace(word, '');
		#    com2 = com2.replace(word, '');
		
		
		
		try:
			com1 = link(com1, entity_dict)
			if com1 == None or com1 == '':
			    continue
		except:
			pass

		for c in com2.split(','):
			try:
				c = link(c, entity_dict)
				if c == None or c == '':
				    continue
			except:
				pass
			
			print (com1+','+c)
		#fout.write((com1 + "," + c))
	#fout.close()
