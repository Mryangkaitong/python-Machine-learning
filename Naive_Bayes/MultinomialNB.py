#详细地址请见：https://www.jianshu.com/p/845b16559431
import warnings
import numpy as np
from sklearn import metrics
from scipy.stats import sem
from sklearn.pipeline import Pipeline
from sklearn.datasets import fetch_20newsgroups
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer, CountVectorizer

#忽略一些版本不兼容等警告
warnings.filterwarnings("ignore")
from sklearn.cross_validation import cross_val_score, KFold


news = fetch_20newsgroups(subset='all')

'''
#测试news,来了解数据集的构成
print (news.keys())
print (type(news.data), type(news.target), type(news.target_names))
print (news.target_names)
print(news.data[0])
print(news.target_names[news.target[0]])
print (len(news.data))
print (len(news.target))

'''

#原样本有18846个，为了运行快这里只抽取了样本中的188个样本进行实验，即用x_Reduced_sample1，y_Reduced_sample1进行实验
x_Reduced_sample1, x_Reduced_sample2 , y_Reduced_sample1, y_Reduced_sample2 = train_test_split(news.data, news.target, test_size = 0.99)

#划分训练集和测试集(76个)
x_train, x_test, y_train, y_test = train_test_split(x_Reduced_sample1, y_Reduced_sample1, test_size = 0.4)


#pipeline来将多个学习器组成流水线，通常流水线的形式为： 
#将数据标准化的学习器---特征提取的学习器---执行预测的学习器
#除了最后一个学习器之外，前面的所有学习器必须提供transform方法，该方法用于数据转化(例如：归一化，正则化，以及特征提取)
# CountVectorizer,HashingVectorizer,TfidfVectorizer是三种构建特征向量的工具
nbc_1 = Pipeline([
    ('vect', CountVectorizer()),
    ('clf', MultinomialNB()),
                ])
warnings.filterwarnings("ignore")
nbc_2 = Pipeline([
    ('vect', HashingVectorizer(non_negative=True)),
    ('clf', MultinomialNB()),
                ])
nbc_3 = Pipeline([
    ('vect', TfidfVectorizer()),
    ('clf', MultinomialNB()),
                ])
nbcs=[nbc_1, nbc_2, nbc_3]


#分类评价机制:k-折叠交叉验证
def evaluate_cross_validation(clf, X, y, K):
    # 最基础的CV算法，也是默认采用的CV策略，地址见http://blog.sina.com.cn/s/blog_7103b28a0102w70h.html
    cv = KFold(len(y), n_folds=K, shuffle=True, random_state=0)
    # k-折叠交叉验证地址见https://blog.csdn.net/evillist/article/details/61912827
    scores = cross_val_score(clf, X, y, cv=cv)
    #换分K组后每组的准确率(是一个数组)
    print(scores)
    #数组中准确率的平均值(越高越好)
    print(np.mean(scores))
    #数组中准确率平的均值标准误差。
    print(sem(scores))

#测试CountVectorizer,HashingVectorizer,TfidfVectorizer是三种构建特征向量的工具的性能
for nbc in nbcs:
    evaluate_cross_validation(nbc, x_train, y_train, 5)


'''

#优化特征提取提高分类的效果系列

#1:TfidfVectorizer的一个参数token_pattern用于指定提取单词的规则
#  默认的正则表达式是ur"\b\w\w+\b"，这个正则表达式只匹配单词边界并考虑到了下划线，也可能考虑到了横杠和点。
#  新的正则表达式是ur"\b[a-z0-9_\-\.]+[a-z][a-z0-9_\-\.]+\b"
#2:TfidfVectorizer的一个参数stop_words这个参数指定的词将被省略不计入到标记词的列表中，
#  比如一些出现频率很高的词(英文中的a或者and等),但是这些词对于特定的主题不能提供任何的先验支持。
#3:MultinomialNB有一个alpha参数，该参数是一个平滑参数，默认是1.0，我们将其设为0.01
#!!!!!!!!!!但是1和2方案运行不通过不知道什么原因，去掉就可以
def get_stop_words():
    result = set()
    for line in open('stopwords_en.txt', 'r').readlines():
        result.add(line.strip())
    return result
stop_words= get_stop_words()
print(stop_words)
nbc_4 = Pipeline([
    ('vect', TfidfVectorizer(
                stop_words=stop_words,                                  #运行时去掉才行(不知道为什么？)
                token_pattern='ur\b[a-z0-9_\-\.]+[a-z][a-z0-9_\-\.]+\b',#运行时去掉才行(不知道为什么？)   
    )),
    ('clf', MultinomialNB(alpha=0.01)),
                ])

evaluate_cross_validation(nbc_4,x_train, y_train, 5)

'''
#fit_prior：布尔型，可选项，默认True，表示是否学习先验概率，参数为False表示所有类标记具有相同的先验概率
#class_prior：类似数组，数组大小为(n_classes,)，默认None，是先验概率的值
#具体见https://blog.csdn.net/kancy110/article/details/72763276
nbc_5 = Pipeline([
    ('vect', TfidfVectorizer()),
    ('clf', MultinomialNB(alpha=0.01, class_prior=None, fit_prior=True)),
                ])
#核心代码
nbc_5.fit(x_train,y_train)
y_predict = nbc_5.predict(x_test)

print(nbc_5.score(x_test, y_test))                     #预测准确率
print(metrics.classification_report(y_test,y_predict)) #包含准确率，召回率等信息表
print(metrics.confusion_matrix(y_test,y_predict))       #混淆矩阵

'''
正如https://blog.csdn.net/kancy110/article/details/72763276介绍的那样如果有的场景直接用
MultinomialNB()时就可以完成任务，而不是先通过构建特征向量的工具时，学习后的模型还有很多参数可以看
包括:
class_log_prior_：各类标记的平滑先验概率对数值，其取值会受fit_prior和class_prior参数的影响
intercept_：将多项式朴素贝叶斯解释的class_log_prior_映射为线性模型，其值和class_log_propr相同
feature_log_prob_：指定类的各特征概率(条件概率)对数值，返回形状为(n_classes, n_features)数组
等等

'''


