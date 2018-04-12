import numpy as np  
import scipy as sp  
from sklearn import tree  
from sklearn.metrics import precision_recall_curve  
#决策树的基本操作
from sklearn.metrics import classification_report  
from sklearn.model_selection import train_test_split
#数据读入 
data   = []  
labels = []  
with open("source _data.txt") as ifile:  
        for line in ifile:  
            tokens = line.strip().split(' ')  
            data.append([float(tk) for tk in tokens[:-1]])  
            labels.append(tokens[-1])  
x = np.array(data)  
labels = np.array(labels)  
y = np.zeros(labels.shape)  
  
  
#标签转换为0/1   
y[labels=='fat']=1  
  
# 拆分训练数据与测试数据   
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.4)  
  
# 核心代码：使用信息熵作为划分标准，对决策树进行训练 
clf = tree.DecisionTreeClassifier(criterion='entropy')   
clf.fit(x_train, y_train)

#系数反映每个特征的影响力。越大表示该特征在分类中起到的作用越大
print(clf.feature_importances_)


#将学习树结构导出到tree.dot文件
with open("tree.dot", 'w') as f:
    f = tree.export_graphviz(clf, out_file=f)


#预测结果
answer = clf.predict(x_train)
answer_proba = clf.predict_proba(x_train)#计算属于每个类的概率
print(answer)
print(answer_proba)

#sklearn中的classification_report函数用于显示主要分类指标的文本报告
#具体见https://blog.csdn.net/akadiao/article/details/78788864
answer = clf.predict(x) 
print(classification_report(y, answer, target_names = ['thin', 'fat']))


