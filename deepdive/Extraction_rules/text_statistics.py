import os
import re
import pyltp
import argparse
import warnings
import pandas as pd
from tqdm import tqdm, tqdm_notebook
from sklearn.externals.joblib import Parallel, delayed
from textrank4zh import TextRank4Keyword, TextRank4Sentence
#tqdm_notebook().pandas()
warnings.filterwarnings("ignore")

#不能写在类里面，否则会报错
def extract_article(df,company_1_list,company_2_list):
        text = df['text'].tolist()[0]
        #zip是一个迭代器，只有第一次才有值
        for company_1,company_2 in zip(company_1_list,company_2_list):
            if company_1 in text and company_2 in text:
                df['company_1'] = company_1
                df['company_2'] = company_2
                #分句
                for sent in list(pyltp.SentenceSplitter.split(text)):
                    if company_1 in text and company_2 in sent:
                        df['text'] = sent
                        break
                break
        return df

class Text_statistics(object):
    def __init__(self,articles_filename='articles.csv',record_filename='record.csv',rule_reference_filename='rule_reference.txt',
                LTP_DIR="ltp_data_v3.4.0/",filter_dictionary=['有限公司']):
        
        self.articles_filename = articles_filename
        self.record_filename = record_filename
        self.rule_reference_filename = rule_reference_filename
        ###############################加载ltp相关模型#########################################
        self.LTP_DIR = LTP_DIR
        #分词模型
        self.segmentor = pyltp.Segmentor()
        self.segmentor.load(os.path.join(self.LTP_DIR, "cws.model"))
        #词性模型
        self.postagger = pyltp.Postagger()
        self.postagger.load(os.path.join(self.LTP_DIR, 'pos.model'))
        #命名实体模型
        self.recognizer = pyltp.NamedEntityRecognizer()
        self.recognizer.load(os.path.join(self.LTP_DIR, 'ner.model'))
        #依存句法分析
        self.parser = pyltp.Parser() 
        self.parser.load(os.path.join(self.LTP_DIR, 'parser.model'))
        self.filter_dictionary = filter_dictionary
        
        
        
        
        self.left_postags_dict = {}
        self.left_word_dict = {}
        self.mid_postags_dict = {}
        self.mid_word_dict = {}
        self.right_postags_dict = {}
        self.right_word_dict = {}
        self.CMP_dict = {}
        self.SBV_dict = {}
        self.VOB_dict = {}
    
    def word_frequency(self,words,postags,begin,end,word_dict,postags_dict):
        for index in range(begin,end):
            #去掉停用词
            if words[index] in self.stopwords or words[index] in self.filter_dictionary:
                continue
            else:
                #词频统计
                if words[index] not in word_dict:
                    
                    word_dict[words[index]] = 1
                else:
                    word_dict[words[index]] = word_dict[words[index]]+1
                    #依据词性统计
                if postags[index] not in  postags_dict:
                    dict_tmp = {}
                    dict_tmp[words[index]] = 1
                    postags_dict[postags[index]] = dict_tmp
                else:
                    if words[index] not in postags_dict[postags[index]]:
                        postags_dict[postags[index]][words[index]] = 1
                    else:
                        postags_dict[postags[index]][words[index]] = postags_dict[postags[index]][words[index]]+1
                        
    def word_frequency_to_file(self,word_title,postags_title,word_dict,postags_dict,num_word_frequency,num_postags_word_frequency):
        with open(self.rule_reference_filename, "a") as f:
            word_dict = sorted(word_dict.items(),reverse=True,key=lambda x:x[1])
            f.write(word_title+'\n') 
            i = 0
            for word,frequency in word_dict:
                if i<=num_word_frequency-1:
                    f.write(word+'\t'+str(frequency)+'\n')
                else:
                    break
                i = i+1
            f.write(postags_title+'\n')
            for key in postags_dict.keys():
                f.write(key+'\t')
                temp_dict = sorted(postags_dict[key].items(),reverse=True,key=lambda x:x[1])
                i = 0
                for word,frequency in temp_dict:
                    if i<=num_postags_word_frequency-1:
                        f.write(word+':'+str(frequency)+' ')
                    else:
                        break
                    i = i+1
                f.write('\n')
                
    def parser_to_file(self,parser_dict,num_parse_frequency,title):
         with open(self.rule_reference_filename, "a") as f:
            parser_dict = sorted(parser_dict.items(),reverse=True,key=lambda x:x[1])
            f.write(title+'\n')  
            i = 0
            for word,frequency in parser_dict:
                if i<=num_parse_frequency:
                    f.write(word+'\t'+str(frequency)+'\n')
                else:
                    break
                i = i+1
                    
    def load_data(self):
        #####################################加载数据###########################################
        articles = pd.read_csv(self.articles_filename,header=None)
        record = pd.read_csv(self.record_filename,header=None)
        record.columns = ['company_1','company_2']
        articles.columns = ['id','text']
        print('文本总数：%d'%(articles.shape[0]))
        print('标签总数：%d'%(record.shape[0]))
        #####################################加载停用词###########################################
        #停用词下载https://github.com/goto456/stopwords
        self.stopwords = []
        with open(os.path.join(self.LTP_DIR, "stopwords.txt"), 'r') as fr:
            for line in fr:
                self.stopwords.append(line.strip())
        print('停用词个数：%d'%(len(self.stopwords)))
        ##################################筛选出有关系的文本句子##############################################
        print('筛选出有关系的句子中......................')
        self.company_1_list = record['company_1'].tolist()
        self.company_2_list = record['company_2'].tolist()
        articles['company_1'] = 'NA'
        articles['company_2'] = 'NA'

        articles = articles.groupby(articles.index)
        retlist = Parallel(n_jobs=4)(delayed(extract_article)(group,self.company_1_list,self.company_2_list) for name, group in tqdm(articles))
        articles = pd.concat(retlist)
        articles = articles[articles['company_1']!='NA']
        self.article_list = articles['text'].tolist()
        self.company_1_list = articles['company_1'].tolist()
        self.company_2_list = articles['company_2'].tolist()
        del record
        del articles
        print('根据标签抽取出有关系的句子数：%d'%(len(self.article_list)))

    ###########################################提取关键词,短语，句子######################################################
    #textrank4zh:textRank算法
    #参考：https://blog.csdn.net/wotui1842/article/details/80351386
    def extract_key_information(self,num_key_word=30,num_key_phrase=20,num_key_sentence=5):
        text=''.join(self.article_list)
        # 创建分词类的实例
        tr4w = TextRank4Keyword()
        # 对文本进行分析，设定窗口大小为2，并将英文单词小写
        tr4w.analyze(text=text, lower=True, window=2)
        with open(self.rule_reference_filename, "a") as f:
            # 从关键词列表中获取前20个关键词
            f.write('###########################关 键 词##################################'+'\n')
            for item in tr4w.get_keywords(num=num_key_word, word_min_len=1):
                if item.word in self.stopwords or item.word in self.filter_dictionary:
                    continue
                else:
                    f.write(item.word+'\t'+str(item.weight)+'\n')
        with open(self.rule_reference_filename, "a") as f:
            # 从关键短语列表中获取20个关键短语
            f.write('##########################关 键 短 语##################################'+'\n')
            for phrase in tr4w.get_keyphrases(keywords_num=num_key_phrase, min_occur_num=2):
                f.write(phrase+'\n')      
        # 创建分句类的实例
        tr4s = TextRank4Sentence()
        # 英文单词小写，进行词性过滤并剔除停用词
        tr4s.analyze(text=text, lower=True, source='all_filters')
        with open(self.rule_reference_filename, "a") as f:
            # 从关键短语列表中获取5关键短语
            f.write('###########################关 键 句##################################'+'\n')
            for item in tr4s.get_key_sentences(num=num_key_sentence):
                f.write(str(item.index)+str(item.weight)+str(item.sentence)+'\n')
                f.write('----------------'+'\n') 
    ###########################################句法分析######################################################
    #pyltp包：https://www.jianshu.com/p/867478f0e674
    #https://blog.csdn.net/huangqihao723/article/details/79039405
    #http://ltp.ai/docs/appendix.html#id3
    def extract_semantic(self,num_word_frequency=6,num_postags_word_frequency=5,num_parse_frequency=15):
        for sentence,c1,c2 in zip(self.article_list,self.company_1_list,self.company_2_list):
            c1_begin = []
            c1_end = []
            c2_begin = []
            c2_end = []
            #分词
            words = list(self.segmentor.segment(sentence))
            #词性
            postags = list(self.postagger.postag(words))
            #命名实体
            nertags = list(self.recognizer.recognize(words, postags))
            #寻找当前实体对的最远位置
            first_indexes = (i for i in range(len(nertags)) if "-Ni" in nertags[i]  and (i == 0 or "-Ni" not in nertags[i-1]) 
                             and re.match(u'^[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ffa-zA-Z]+$', str(words[i])) != None)
            for begin_index in first_indexes:
                end_index = begin_index + 1
                while end_index < len(nertags) and "-Ni" in nertags[end_index]  and re.match(u'^[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ffa-zA-Z]+$', str(words[end_index])) != None:
                    end_index += 1
                if  ''.join(words[begin_index:end_index])== c1:
                    c1_begin.append(begin_index)
                    c1_end.append(end_index-1)
                elif ''.join(words[begin_index:end_index]) in c1:
                    end_index_tmp = end_index
                    while ''.join(words[begin_index:end_index_tmp]) in c1:    
                        end_index_tmp+=1
                        if ''.join(words[begin_index:end_index_tmp])==c1:    
                            c1_begin.append(begin_index)
                            c1_end.append(end_index_tmp-1)
                            break
                elif  ''.join(words[begin_index:end_index])== c2:
                    c2_begin.append(begin_index)
                    c2_end.append(end_index-1)
                elif ''.join(words[begin_index:end_index]) in c2:
                    end_index_tmp = end_index
                    while ''.join(words[begin_index:end_index_tmp]) in c2:    
                        end_index_tmp+=1
                        if ''.join(words[begin_index:end_index_tmp])==c2:    
                            c2_begin.append(begin_index)
                            c2_end.append(end_index_tmp-1)
                            break
                else:
                    continue
            #有可能是一些人名
            try:
                c1_begin_min = min(c1_begin+c2_begin)
                c1_end_min = min(c1_end+c2_end)
                c2_begin_max= max(c1_begin+c2_begin)
                c2_end_max = max(c1_end+c2_end)
            except:
                print(c1,c2)
                print(sentence)
                print('********')
                continue

            #####################################词频############################################
            #left
            self.word_frequency(words,postags,0,c1_begin_min,self.left_word_dict,self.left_postags_dict)
            #mid
            self.word_frequency(words,postags,c1_end_min+1,c2_begin_max,self.mid_word_dict,self.mid_postags_dict)
            #right
            self.word_frequency(words,postags,c2_end_max+1,len(words),self.right_word_dict,self.right_postags_dict)
           
            arcs = self.parser.parse(words[c1_begin_min:c2_end_max+1], postags[c1_begin_min:c2_end_max+1])  # 句法分析
            rely_id = [arc.head for arc in arcs]    # 提取依存父节点id
            relation = [arc.relation for arc in arcs]   # 提取依存关系
            heads = ['Root' if id == 0 else words[id-1] for id in rely_id]  # 匹配依存父节点词语
            #####################################句法分析############################################
            for i in range(len(words[c1_begin_min:c2_end_max+1])):
                if relation[i] == 'CMP':
                    if words[c1_begin_min+i] + ', ' + heads[i] not in self.CMP_dict:
                        self.CMP_dict[words[c1_begin_min+i] + ', ' + heads[i]] = 1
                    else:
                        self.CMP_dict[words[c1_begin_min+i] + ', ' + heads[i]] = self.CMP_dict[words[c1_begin_min+i] + ', ' + heads[i]]+1
                elif relation[i] == 'SBV':
                    if words[c1_begin_min+i] + ', ' + heads[i] not in self.SBV_dict:
                        self.SBV_dict[words[c1_begin_min+i] + ', ' + heads[i]] = 1
                    else:
                        self.SBV_dict[words[c1_begin_min+i] + ', ' + heads[i]] = self.SBV_dict[words[c1_begin_min+i] + ', ' + heads[i]]+1
                elif relation[i] == 'VOB':
                    if words[c1_begin_min+i] + ', ' + heads[i] not in self.VOB_dict:
                        self.VOB_dict[words[c1_begin_min+i] + ', ' + heads[i]] = 1
                    else:
                        self.VOB_dict[words[c1_begin_min+i] + ', ' + heads[i]] = self.VOB_dict[words[c1_begin_min+i] + ', ' + heads[i]]+1
                else:
                    continue
        #####################################将结果写入txt############################################
        #left
        self.word_frequency_to_file('#'*27+'左半部分词频'+'#'*27,'#'*27+'左半部分词性词频'+'#'*27,
                                    self.left_word_dict,self.left_postags_dict,num_word_frequency,num_word_frequency)
        #mid
        self.word_frequency_to_file('#'*27+'中间部分词频'+'#'*27,'#'*27+'中间部分词性词频'+'#'*27,
                                    self.mid_word_dict,self.mid_postags_dict,num_word_frequency,num_word_frequency)
        #right
        self.word_frequency_to_file('#'*27+'右半部分词频'+'#'*27,'#'*27+'右半部分词性词频'+'#'*27,
                                    self.right_word_dict,self.right_postags_dict,num_word_frequency,num_word_frequency)
        #句法
        self.parser_to_file(self.SBV_dict,num_parse_frequency,'#'*27+'实体对中间主谓短语'+'#'*27)
        self.parser_to_file(self.CMP_dict,num_parse_frequency,'#'*27+'实体对中间动补短语'+'#'*27)
        self.parser_to_file(self.VOB_dict,num_parse_frequency,'#'*27+'实体对中间动宾短语'+'#'*27)
def main():
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-input_articles',type=str,default ='articles.csv')
    parser.add_argument('-input_record',type=str,default='record.csv')
    parser.add_argument('-output_file',type=str, default='rule_reference.txt')
    parser.add_argument('-ltp_model', type=str, default='ltp_data_v3.4.0/')
    args = parser.parse_args()
    filter_dictionary = ['公司','有限公司','股份','支行','银行','集团','有限责任','子公司','分行','内容']
    Ts = Text_statistics(articles_filename=args.input_articles,record_filename=args.input_record,
                         rule_reference_filename=args.output_file,LTP_DIR=args.ltp_model,filter_dictionary=filter_dictionary)
    print('*'*27+'加载数据'+'*'*27)
    Ts.load_data()
    print('*'*27+'抽取一些关键词频，短语等信息'+'*'*27)
    Ts.extract_semantic()
    print('*'*27+'抽取一些关键信息'+'*'*27)
    Ts.extract_key_information()
    print('全部完成')
if __name__ == '__main__':
    main()
