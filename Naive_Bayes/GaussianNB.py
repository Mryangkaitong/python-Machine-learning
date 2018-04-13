#GaussianNB(高斯)类
from sklearn import datasets
from sklearn.naive_bayes import GaussianNB
import numpy as np
iris=datasets.load_iris()

#核心代码:其实fit后面还有一个参数即fit(X, y, sample_weight=None),sample_weight表各样本权重数组，假如一共训练8个样本
#则可以写为clf.fit(iris.data[:8], iris.target[:8],sample_weight=np.array([0.05,0.05,0.1,0.1,0.1,0.2,0.2,0.2]))
clf=GaussianNB()
clf.fit(iris.data,iris.target)


'''
#GaussianNB一个重要的功能是有 partial_fit方法，这个方法的一般用在如果训练集数据量非常大，一次不能全部载入
#内存的时候。这时我们可以把训练集分成若干等分，重复调用partial_fit来一步步的学习训练集，非常方便
#在第一次调用partial_fit函数时，必须制定classes参数，在随后的调用可以忽略
clf.partial_fit(iris.data, iris.target,classes=[0,1,2])

'''

#学习后模型中的一些参数
clf.set_params(priors=[0.333, 0.333, 0.333])#这里要设一下各个类标记对应的先验概率，如果不设置直接clf.priors返回的是None(不知道为什么？)
print(clf.priors)                           #获取各个类标记对应的先验概率
print(clf.class_prior_ )                    #同priors一样，都是获取各个类标记对应的先验概率，区别在于priors属性返回列表，class_prior_返回的是数组
print(clf.get_params(deep=True))            #返回priors与其参数值组成字典

print(clf.class_count_)                     #获取各类标记对应的训练样本数
print(clf.theta_)                           #获取各个类标记在各个特征上的均值
print(clf.sigma_)                           #获取各个类标记在各个特征上的方差



#测试数据
data_test=np.array([6,4,6,2])
data=data_test.reshape(1,-1)
Result_predict=clf.predict(data)
Score=clf.score([[6,8,5,3],[5,3,4,2],[4,6,7,2]],[2,0,1],sample_weight=[0.3,0.5,0.2])

Result_predict_proba=clf.predict_proba(data)
Result_predict_log_proba=clf.predict_log_proba(data)
print(Result_predict)                                                               #预测所属类别
print(Result_predict_proba)                                                         #输出测试样本在各个类标记上预测概率值
print(Result_predict_log_proba)                                                     #输出测试样本在各个类标记上预测概率值对应对数值
print(Score)                                                                        #返回测试样本映射到指定类标记上的得分(准确率)
