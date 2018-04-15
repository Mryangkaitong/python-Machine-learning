#RandomForestClassifier
import math
import matplotlib as mpl
import warnings
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.datasets import make_blobs
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

#忽略一些版本不兼容等警告
warnings.filterwarnings("ignore")

#源数据产生具体看https://blog.csdn.net/ichuzhen/article/details/51768934
n_features=2  #每个样本有几个属性或特征
x,y = make_blobs(n_samples=300, n_features=n_features, centers=6)
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=1, train_size=0.7)

#核心代码
#传统决策树、随机森林算法、极端随机树关于区别:https://blog.csdn.net/hanss2/article/details/53525503
#关于其中参数的说明请看http://www.jb51.net/article/131172.htm
clf1 = DecisionTreeClassifier(max_depth=None, min_samples_split=2,random_state=0)
clf2 = RandomForestClassifier(n_estimators=10,max_features=math.sqrt(n_features), max_depth=None,min_samples_split=2, bootstrap=True)
clf3 = ExtraTreesClassifier(n_estimators=10,max_features=math.sqrt(n_features), max_depth=None,min_samples_split=2, bootstrap=False)



'''
#交叉验证
scores1 = cross_val_score(clf1, x_train, y_train)
scores2 = cross_val_score(clf2, x_train, y_train)
scores3 = cross_val_score(clf3, x_train, y_train)
print('DecisionTreeClassifier交叉验证准确率为:'+str(scores1.mean()))    
print('RandomForestClassifier交叉验证准确率为:'+str(scores2.mean()))    
print('ExtraTreesClassifier交叉验证准确率为:'+str(scores3.mean()))
'''





clf1.fit(x_train, y_train)
clf2.fit(x_train, y_train)
clf3.fit(x_train, y_train)

#区域预测
x1_min, x1_max = x[:, 0].min(), x[:, 0].max()            # 第0列的范围
x2_min, x2_max = x[:, 1].min(), x[:, 1].max()            # 第1列的范围
x1, x2 = np.mgrid[x1_min:x1_max:200j, x2_min:x2_max:200j]# 生成网格采样点行列均为200点
area_smaple_point = np.stack((x1.flat, x2.flat), axis=1) # 将区域划分为一系列测试点去用学习的模型预测，进而根据预测结果画区域
area1_predict = clf1.predict(area_smaple_point)          # 所有区域点进行预测
area1_predict = area1_predict.reshape(x1.shape)          # 转化为和x1一样的数组因为用plt.pcolormesh(x1, x2, area_flag, cmap=classifier_area_color) 
                                                         # 时x1和x2组成的是200*200矩阵，area_flag要与它对应

area2_predict = clf2.predict(area_smaple_point)          
area2_predict = area2_predict.reshape(x1.shape)

area3_predict = clf3.predict(area_smaple_point)          
area3_predict = area3_predict.reshape(x1.shape)



mpl.rcParams['font.sans-serif'] = [u'SimHei']            #用来正常显示中文标签    
mpl.rcParams['axes.unicode_minus'] = False               #用来正常显示负号

classifier_area_color = mpl.colors.ListedColormap(['#A0FFA0', '#FFA0A0', '#A0A0FF'])  #区域颜色
cm_dark = mpl.colors.ListedColormap(['g', 'r', 'b'])                                  #样本所属类别颜色


#绘图
#第一个子图
plt.subplot(2,2,1)

plt.pcolormesh(x1, x2, area1_predict, cmap=classifier_area_color)                        
plt.scatter(x_train[:,0], x_train[:,1], c=y_train,marker='o', s=50, cmap=cm_dark)    
plt.scatter(x_test[:,0],x_test[:,1], c=y_test,marker='x', s=50, cmap=cm_dark)

plt.xlabel('data_x', fontsize=8)  
plt.ylabel('data_y', fontsize=8)
plt.xlim(x1_min, x1_max)  
plt.ylim(x2_min, x2_max)
plt.title(u'DecisionTreeClassifier:传统决策树', fontsize=8)
plt.text(x1_max-9, x2_max-2, u'$o---train ; x---test$')


#第二个子图
plt.subplot(2,2,2)

plt.pcolormesh(x1, x2, area2_predict, cmap=classifier_area_color)                        
plt.scatter(x_train[:,0], x_train[:,1], c=y_train,marker='o', s=50, cmap=cm_dark)    
plt.scatter(x_test[:,0],x_test[:,1], c=y_test,marker='x', s=50, cmap=cm_dark)

plt.xlabel('data_x', fontsize=8)  
plt.ylabel('data_y', fontsize=8)
plt.xlim(x1_min, x1_max)  
plt.ylim(x2_min, x2_max)
plt.title(u'RandomForestClassifier:随机森林算法', fontsize=8)
plt.text(x1_max-9,x2_max-2, u'$o---train ; x---test$')


#第三个子图
plt.subplot(2,2,3)

plt.pcolormesh(x1, x2, area3_predict, cmap=classifier_area_color)                        
plt.scatter(x_train[:,0], x_train[:,1], c=y_train,marker='o', s=50, cmap=cm_dark)    
plt.scatter(x_test[:,0],x_test[:,1], c=y_test,marker='x', s=50, cmap=cm_dark)

plt.xlabel('data_x', fontsize=8)  
plt.ylabel('data_y', fontsize=8)
plt.xlim(x1_min, x1_max)  
plt.ylim(x2_min, x2_max)
plt.title(u'ExtraTreesClassifier:极端随机树', fontsize=8)
plt.text(x1_max-9, x2_max-2, u'$o---train ; x---test$')


#第四个子图
plt.subplot(2,2,4)
y=[]
scores1 = cross_val_score(clf1, x_train, y_train)
y.append(scores1.mean())
scores2 = cross_val_score(clf2, x_train, y_train)
y.append(scores2.mean())
scores3 = cross_val_score(clf3, x_train, y_train)
y.append(scores3.mean())

x=[0,1,2]
plt.bar(x,y,0.4,color="green")  
plt.xlabel("0--DecisionTreeClassifier;1--RandomForestClassifier;2--ExtraTreesClassifie", fontsize=8)  
plt.ylabel("平均准确率", fontsize=8)
plt.ylim(0.9, 0.99)
plt.title("交叉验证",fontsize=8)
for a, b in zip(x, y):  
    plt.text(a, b, b, ha='center', va='bottom', fontsize=10)

plt.show()

