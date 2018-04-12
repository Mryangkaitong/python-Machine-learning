#利用iris数据源来预测所属花的种类
from sklearn import datasets
import os
import numpy as np  
import scipy as sp  
from sklearn import tree  
from sklearn.metrics import precision_recall_curve  
from sklearn.metrics import classification_report  
from sklearn.model_selection import train_test_split

iris=datasets.load_iris()
x=np.array(iris.data)
y=np.array(iris.target)
  
# 拆分训练数据与测试数据,test_size代表学习样本占的比例，越大学习的结果越准确
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.8)  
  
# 核心代码：使用信息熵作为划分标准，对决策树进行训练 
clf = tree.DecisionTreeClassifier(criterion='entropy')   
clf.fit(x_train, y_train)

#系数反映每个特征的影响力。越大表示该特征在分类中起到的作用越大
print(clf.feature_importances_)

#预测
answer = clf.predict(x_train)
print(answer)

#sklearn中的classification_report函数用于显示主要分类指标的文本报告
#具体见https://blog.csdn.net/akadiao/article/details/78788864
answer = clf.predict(x) 
print(classification_report(y, answer, target_names = ['V','C','D']))

