#!/usr/bin/env python3
#encoding:utf-8
import os
import sys
import psycopg2
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import  f1_score
from sklearn.metrics import roc_auc_score

matplotlib.use('Agg')
test_size = int(sys.argv[-1])
column_list = ['relation','probability_threshold','Precision','Accuracy','Recall','F1','Auc']
baseDir = os.path.dirname(os.path.abspath(__name__))+'/Performance_evaluation/'
if not os.path.exists(baseDir):
    os.makedirs(baseDir)

result = pd.DataFrame(columns=column_list)
result_save_path = baseDir+"Performance_evaluation.csv"
conn = psycopg2.connect(database=sys.argv[1],host="127.0.0.1",port="5432")

#遍历每一种关系
for index,relation in enumerate(sys.argv[2:-1]):
    plt.figure(index+1,figsize=(10, 10))
    fig_save_path = baseDir+relation+".png"
    fig_title_name = relation+":Performance evaluation with different probability threshold"
    df_prediction_sql = "select * from "+"has_"+relation+"_label_inference"
    df_company_name_sql = "select * from "+relation+"_candidate"
    df_train_test_sql = "select * from "+relation+"_label_test_train"

    #加载所需数据表
    try:
        df_prediction = pd.read_sql(df_prediction_sql,con=conn)
    except:
        print("注意: 加载"+relation+"_label_inference"+"表时出错！！！！！！")
        print("故结果不能生成"+relation+"关系有关的性能图")
        continue
    try:
        df_company_name = pd.read_sql(df_company_name_sql,con=conn)
    except:
        print("注意: 加载"+relation+"_candidate"+"表时出错！！！！！！")
        print("故结果不能生成"+relation+"关系有关的性能图")
        continue
    try:
        df_train_test = pd.read_sql(df_train_test_sql,con=conn)
    except:
        print("注意: 加载"+relation+"_label_test_train"+"表时出错！！！！！！")
        print("故结果不能生成"+relation+"关系有关的性能图")
        continue

    #筛选出测试集的预测结果
    #df_prediction = df_prediction[df_prediction['label'].isna()]
    df_test = df_train_test[df_train_test['test_train_flag']<=test_size]
    df_test_prediction = pd.merge(df_test, df_prediction, how='left', on=['p1_id', 'p2_id'])
    df_test_prediction = pd.merge(df_test_prediction, df_company_name, how='left', on=['p1_id', 'p2_id'])
    df_test_prediction = df_test_prediction[df_test_prediction['vote_sum']!=0]

    #针对实体对中文名去重
    df_test_prediction = df_test_prediction.groupby([df_test_prediction['p1_name'], df_test_prediction['p2_name']]).apply(lambda t: t[t.expectation==t.expectation.max()])

    #计算真实标签和预测标签
    df_test_prediction['y_true'] = df_test_prediction['vote_sum'].apply(lambda x:1 if x>0 else 0)
    y_true = df_test_prediction['y_true'].values
    y_pred_probability = df_test_prediction['expectation'].values
    relation_list = []
    probability_threshold = []
    Accuracy = []
    Recall = []
    Precision = []
    Auc = []
    F1 = []
    #遍历阈值
    for probability_threshold_cur in range(0,100,1):
        probability_threshold_cur = float(probability_threshold_cur/100)
        relation_list.append(relation)
        probability_threshold.append(probability_threshold_cur)
        df_test_prediction['y_pred'] = df_test_prediction['expectation'].apply(lambda x:1 if x>=probability_threshold_cur else 0)
        y_pred = df_test_prediction['y_pred'].values
        #相关指标
        Accuracy.append(accuracy_score(y_true, y_pred))
        Recall.append(recall_score(y_true, y_pred, average='macro'))
        Precision.append(precision_score(y_true, y_pred, average='binary'))
        F1.append(f1_score(y_true, y_pred, average='binary'))
        Auc.append(roc_auc_score(y_true, y_pred_probability))
    Accuracy_probability_threshold_best = probability_threshold[np.argmax(np.array(Accuracy))]
    Recall_probability_threshold_best = probability_threshold[np.argmax(np.array(Recall))]
    Precision_probability_threshold_best = probability_threshold[np.argmax(np.array(Precision))]
    Auc_probability_threshold_best = probability_threshold[np.argmax(np.array(Auc))]
    F1_probability_threshold_best = probability_threshold[np.argmax(np.array(F1))]

    #绘图
    fig_Accuracy_label = "Accuracy : "+"best probability_threshold is "+str(Accuracy_probability_threshold_best)
    fig_Precision_label = "Precision : "+"best probability_threshold is "+str(Precision_probability_threshold_best)
    fig_Recall_label = "Recall : "+"best probability_threshold is "+str(Recall_probability_threshold_best)
    fig_F1_label = "F1 : "+"best probability_threshold is "+str(F1_probability_threshold_best)
                        
    plt.plot(probability_threshold, Accuracy, c='r',marker='o',label=fig_Accuracy_label)
    plt.plot(probability_threshold, Precision, c='c',marker='o',label=fig_Precision_label)
    plt.plot(probability_threshold, Recall, c='b',marker='o',label=fig_Recall_label)
    plt.plot(probability_threshold, F1, c='g',marker='o',label=fig_F1_label)
    plt.plot(probability_threshold, Auc, c='y',marker='o',label='Auc')
    plt.title(fig_title_name)
    plt.xlabel("probability threshold")
    plt.ylim(0,1)
    plt.legend()
    plt.savefig(fig_save_path)
    
    #csv结果
    result_cur = pd.DataFrame({'relation':relation_list,'probability_threshold':probability_threshold,'Precision':Precision,
                          'Accuracy':Accuracy,'Recall':Recall,'F1':F1,'Auc':Auc})
    result = result.append(result_cur)
    
    
#调整列的顺序并保存   
result = result[column_list]    
result.to_csv(result_save_path,index=False)
    
    
    
    
    
    
    
    
    
    
    
    
    