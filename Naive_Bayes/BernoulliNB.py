#伯努利朴素贝叶斯算法:类似于多项式朴素贝叶斯，也主要用户离散特征分类，
#和MultinomialNB的区别是：MultinomialNB以出现的次数为特征值，而BernoulliNB的特征值为二进制或布尔型特性
import numpy as np  
from sklearn.naive_bayes import BernoulliNB
x=np.array([[1,2,3,4],[1,3,4,4],[2,4,5,5],[5,6,9,8]])  
y=np.array([1,1,2,3])

#核心代码
clf=BernoulliNB(alpha=2.0,binarize = 3.0,fit_prior=True)
clf.fit(x,y)

'''
#训练后学习模型中的参数
print(np.log(2/4))
print(np.log(1/4))
print(np.log(1/4))
print(clf.class_log_prior_)   #对比上面，这是先验概率对数值，类先验概率等于各类的个数/类的总个数

print(clf.feature_log_prob_ ) #指定类的各特征概率(条件概率)对数值
print(clf.class_count_)       #按类别顺序输出其对应的个数
print(clf.feature_count_)     #各类别各特征值之和，按类的顺序输出，返回形状为[n_classes, n_features] 的数组(不懂？)

'''


#测试数据
x_test=[[1,2,2,5],[7,6,10,9]]                           #数据不能是分数
y_test_predict=clf.predict(x_test)
y_predict_proba=clf.predict_proba(x_test)
y_test_predict_log_proba=clf.predict_log_proba(x_test)
print(y_test_predict)                                   #在测试集x_test上预测，输出x_test对应目标值
print(y_predict_proba)                                  #输出测试样本划分到各个类别的概率值
print(y_test_predict_log_proba)                         #输出测试样本划分到各个类别的概率值的对数
print(clf.score([[3,4,5,4],[1,3,5,6]],[1,3]))           #输出对测试样本的预测准确率的平均值,当然可以加权值这个参数score(X, y, sample_weight=None) 
