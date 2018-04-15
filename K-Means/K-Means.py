#K-Means   
import numpy as np  
import matplotlib.pyplot as plt  
from sklearn.cluster import KMeans
from sklearn.externals import joblib     #模块二
import pandas as pd
import matplotlib as mpl
from scipy.spatial.distance import cdist #模块一
from sklearn import metrics              #模块一

#从磁盘读取城市经纬度数据  
X = []  
f = open('city.txt')  
for v in f:
    X.append([float(v.split(',')[1]),float(v.split(',')[2])])
f.close()

#转换成numpy array,形如:[[1.2 , 3.2],[2.3 , 6.3 ],[1.0 , 2.3]]，转化前X是一个列表
X = np.array(X)

mpl.rcParams['font.sans-serif'] = [u'SimHei']            #绘图时用来正常显示中文标签    
mpl.rcParams['axes.unicode_minus'] = False               #绘图时用来正常显示负号


'''
#模块一：
#通过平均畸变程度来确定类簇的数量,通过轮廓系数(Silhouette Coefficient)评价聚类算法(具体来自https://blog.csdn.net/wangxiaopeng0329/article/details/53542606)
#d=cdist(X,Y,'euclidean')#假设X有M个元素，Y有N个元素，最终会生成M行N列的array，用来计算X、Y中每个相对元素之间的欧拉距离
#numpy.min(d,axis=1) #如果d为m行n列，axis=0时会输出每一列的最小值，axis=1会输出每一行最小值
n_clusters = range(2,5) #假设分别在2,3,4中选取一个最合适的n_clusters
meandistortions=[]
metrics_silhouette=[]
for k in n_clusters:
    clf=KMeans(n_clusters=k)
    cls = clf.fit(X)
    meandistortions.append(sum(np.min(cdist(X,clf.cluster_centers_,'euclidean'),axis=1))/X.shape[0])#平均畸变程度值，越小越好
    metrics_silhouette.append(metrics.silhouette_score(X,clf.labels_,metric='euclidean'))           #轮廓系数,越接近1越好   
#平均畸变程度图   
plt.subplot(121)
plt.plot(n_clusters,meandistortions,'rx-')
plt.xlabel('k')
plt.ylabel('平均畸变程度')
plt.title('K-Means平均畸变程度图(越小越好) ')
#轮廓系数图
plt.subplot(122)
plt.plot(n_clusters,metrics_silhouette,'bx-')
plt.ylabel('轮廓系数')
plt.xlabel('k')
plt.title('K-Means轮廓系数(越接近1越好)')
#显示
plt.show()

'''



'''   

#模块二：
#核心代码:现在把数据和对应的分类放入聚类函数中进行聚类
#其中n_clusters 需要聚成几类，init代表初始点怎么找，max_iter代表迭代次数， n_jobs用的cpu，precompute_distances预先需不需要计算距离
n_clusters=4
clf=KMeans(n_clusters=n_clusters)
cls = clf.fit(X)

#聚类结果的显示,其中用clf和cls均可
print(cls.labels_)                         #显示每个样本所属的簇
print(clf.cluster_centers_)                #4个中心点的坐标
print(clf.inertia_)                        #用来评估簇的个数是否合适，代表所有点到各自中心的距离和，距离越小说明簇分的越好，选取临界点的簇个数
r1 = pd.Series(cls.labels_).value_counts()
print(r1)                                  #统计每个类别下样本个数

#用聚类的学习结果去预测
X1=[[121.35,26.41],[123.5,45.35]]
print(clf.predict(X1))

#保存模型，加载模型(加载后是类别标签)
joblib.dump(clf,'d:/test/km.txt')
clf = joblib.load('d:/test/km.txt')

#画图
markers = ['x','o','*','+']
colors=['b','r','y','g']
for i in range(n_clusters):
     members = cls.labels_ == i
     plt.scatter(X[members,0],X[members,1],s=60,marker=markers[i],c=colors[i],alpha=0.5)
plt.xlabel('经度')
plt.ylabel('纬度')
plt.title('K-Means聚合结果(n_clusters=4)')  
plt.show()

'''
