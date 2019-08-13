import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from collections import Counter

class Preprocess:
    def __init__(self,input_root_path='./data',output_root_path='./data'):
        self.relation_dict_train = {}
        self.relation_dict_dev = {}
        self.input_root_path = input_root_path
        self.output_root_path = output_root_path
        self.id2relation ={'0' :'NA',
                           '1' :'Current_husband',
                           '2' :'ex-husband',
                           '3' :'fiance',
                           '4' :'current_wife',
                           '5' :'ex-wife',
                           '6' :'fiancee',
                           '7' :'grandfather',
                           '8' :'grandmother',
                           '9' :'wai_grandfather',
                           '10':'biological_father',
                           '11':'birth_mother',
                           '12':'son',
                           '13':'daughter',
                           '14':'grandson',
                           '15':'granddaughter',
                           '16':'brother',
                           '17':'younger_brother',
                           '18':'sister',
                           '19':'younger_sister',
                           '20':'uncle',
                           '21':'younger_uncle',
                           '22':'aunt',
                           '23':'nephew',
                           '24':'niece',
                           '25':'Daughter_in_law',
                           '26':'son_in_law',
                           '27':'sister-in-law',
                           '28':'father-in-law',
                           '29':'father-in-law',
                           '30':'friend',
                           '31':'like',
                           '32':'lover',
                           '33':'teacher',
                           '34':'student'}
    #生成rel2id.json
    def generate_rel2id(self,relation2id_file='relation2id.txt'):
        relation2id_dict = {}
        for line in open(os.path.join(self.input_root_path, relation2id_file)):
            relation,relation_id= line.strip().split('\t')
            self.id2relation[relation_id] = relation
    
    def get_relation(self,flag='train'):
        if flag=='train':
            cur_sent2relation_file = 'sent_relation_train.txt'
        else:
            cur_sent2relation_file = 'sent_relation_dev.txt'
        relation_list = []
        most_common_relation = []
        for line in open(os.path.join(self.input_root_path, cur_sent2relation_file)):
            sent_id, relation_id = line.strip().split('\t')
            try:
                _ = int(relation_id)
                if flag=='train':
                    self.relation_dict_train[sent_id] = relation_id
                else:
                    self.relation_dict_dev[sent_id] = relation_id
                relation_list.append(relation_id)
            except:
                print('='*10)
                print('当前句子对应两种id')
                print(sent_id)
                print(relation_id)
                if flag=='train':
                    self.relation_dict_train[sent_id] = relation_id.split()[0]
                else:
                    self.relation_dict_dev[sent_id] = relation_id.split()[0]
                relation_list.append(relation_id.split()[0])
        for key,value in Counter(relation_list).most_common(6):
            if key=='0':
                continue
            else:
                most_common_relation.append(key)
        return most_common_relation
    def common_utils(self,relation_id,file_name,flag='train'):
        result_sent = []
        result_pos_1 = []
        result_pos_2 = []
        result_label = []
        if flag=='train':
            cur_relation_dict = self.relation_dict_train
        else:
            cur_relation_dict = self.relation_dict_dev
        for line in open(os.path.join(self.input_root_path, file_name)):
            #sentence
            sent_id, head, tail, sents = line.strip().split('\t')
            sents = sents.split()
            cur_pos_1 = []
            cur_pos_2 = []
            cur_sent = []
            pos_1 = min(sents.index(head),sents.index(tail))
            pos_2 = max(sents.index(head),sents.index(tail))
            for i,word in enumerate(sents):
                cur_pos_1.append(str(i-pos_1))
                cur_pos_2.append(str(i-pos_2))
                if i==pos_1:
                    cur_sent.append('ENTITY1:{}~{}'.format('person', word))
                elif i==pos_2:
                    cur_sent.append('ENTITY2:{}~{}'.format('person', word))
                else:
                    cur_sent.append(word)
            result_sent.append(' '.join(cur_sent))
            result_pos_1.append(' '.join(cur_pos_1))
            result_pos_2.append(' '.join(cur_pos_2))
            if cur_relation_dict[sent_id]==relation_id:
                result_label.append(1)
            else:
                result_label.append(0)
        result_id = [i+1 for i in range(len(result_sent))]
        c={"id"   : result_id,
           "sent" : result_sent,
           "pos_1": result_pos_1,
           "pos_2": result_pos_2,
           "label": result_label}
        result = pd.DataFrame(c)
        result_positive = result[result['label'] == 1]
        result_negative = result[result['label'] == 0]
        num_positive = float(result_positive.shape[0])
        num_negative = float(result_negative.shape[0])
        frac = num_positive*4/num_negative
        num_negative = result.sample(frac=frac,random_state=3,axis=0)
        result = result_positive.append(num_negative)
        result = result.sample(frac = 1)
        return result
    def generate_dataset(self,relation_id):
        #train_ds
        train_ds = self.common_utils(relation_id,'sent_train.txt')
        relation_dir = os.path.join(self.output_root_path, self.id2relation[relation_id])
        if not os.path.exists(relation_dir):
            os.makedirs(relation_dir)
        train_ds.to_csv (os.path.join(relation_dir,'train_ds.csv') , encoding = "utf-8",header=False,index=False)
        #dev_diag,test_human
        result = self.common_utils(relation_id,'sent_train.txt')
        dev_diag = result.sample(frac=0.6,random_state=3,axis=0)
        test_human = result[~result.index.isin(dev_diag.index)]
        dev_diag.to_csv (os.path.join(relation_dir,'dev_diag.csv') , encoding = "utf-8",header=False,index=False)
        test_human.to_csv (os.path.join(relation_dir,'test_human.csv') , encoding = "utf-8",header=False,index=False)

if __name__ == '__main__':
    pre = Preprocess(input_root_path='./data',output_root_path='./data_test')
    #pre.generate_rel2id()
    print('=============================train 数据集上面句子关系字典=============================')
    most_common_relation_id = pre.get_relation()
    print("==========最多的几种关系：============")
    for i in most_common_relation_id:
        print('%s:%s'%(i,pre.id2relation[i]))
    print('=============================train 数据集上面句子关系字典=============================')
    pre.get_relation('dev')
    print('==============================生成关系对应的train/dev/test============================')
    for i in tqdm(most_common_relation_id):
        pre.generate_dataset(i)
    print("===================================数据预处理成功结束=================================")