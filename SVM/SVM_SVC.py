#支持向量机分类
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import warnings
from sklearn import svm 
from sklearn import metrics
from sklearn import datasets
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split

#忽略一些版本不兼容等警告
warnings.filterwarnings("ignore")

iris=datasets.load_iris()

x=iris.data[:,:2]                                                                        #为了后续的绘图方便只选取了前两个属性进行测试
y=iris.target
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=1, train_size=0.7)

#核心代码 gamma值越高越好，
clf1 = svm.SVC(C=0.8, kernel='rbf', gamma=10, decision_function_shape='ovr')            
clf2 = svm.SVC(C=0.8, kernel='linear',decision_function_shape='ovr')
clf3 = svm.SVC(C=0.8, kernel='rbf', gamma=20, decision_function_shape='ovr')
clf4 = svm.SVC(C=0.8, kernel='rbf', gamma=30, decision_function_shape='ovr')  
clf1.fit(x_train, y_train)
clf2.fit(x_train, y_train)
clf3.fit(x_train, y_train)
clf4.fit(x_train, y_train)

'''
#观察一些参数
y_predict=clf.predict(x_test)
print(clf.decision_function(x_test))                  #decision_function中每一列的值代表距离各类别的距离(正数代表该类，越大越属于该类，负数代表不属于该类)
print(clf.score(x_train, y_train))
print(metrics.classification_report(y_test,y_predict))
print(metrics.confusion_matrix(y_test,y_predict))

'''

#绘图:图中形状为o的点是用来训练学习的学习集，图中形状为x的点为待预测的点
#根据形状为o的点来学习划分出图中区域(用pcolormesh画出),进而根据区域来预测x点，
#图中x点位置和表示类别颜色都是精确的，可以直观的看到预测误差
#注意:从图中来看有可能部分少量o点和x点重合，那是因为学习集合测试集有的数据非常相近
#类如（2.5,3.2）和（2.4,3.1）因为画布间隔问题，看上去就好好想挨着

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

area4_predict = clf4.predict(area_smaple_point)          
area4_predict = area4_predict.reshape(x1.shape)


mpl.rcParams['font.sans-serif'] = [u'SimHei']            #用来正常显示中文标签    
mpl.rcParams['axes.unicode_minus'] = False               #用来正常显示负号

classifier_area_color = mpl.colors.ListedColormap(['#A0FFA0', '#FFA0A0', '#A0A0FF'])  #区域颜色
cm_dark = mpl.colors.ListedColormap(['g', 'r', 'b'])#样本所属类别颜色


#第一个子图采用RBF核
plt.subplot(2,2,1)

plt.pcolormesh(x1, x2, area1_predict, cmap=classifier_area_color)                        
plt.scatter(x_train[:,0], x_train[:,1], c=y_train,marker='o', s=50, cmap=cm_dark)    
plt.scatter(x_test[:,0],x_test[:,1], c=y_test,marker='x', s=50, cmap=cm_dark)

plt.xlabel(iris.feature_names[0]+':花萼的长度', fontsize=8)  
plt.ylabel(iris.feature_names[1]+':花萼的宽度', fontsize=8)
plt.xlim(x1_min, x1_max)  
plt.ylim(x2_min, x2_max)
plt.title(u'SVM_SVC_iris:鸢尾花SVM二特征分类(rbf核gamma=10)', fontsize=8)
plt.text(x1_max-1.5, x1_min-0.1, u'$o---train ; x---test$')
plt.grid(True)


#第二个子图采用Linear核
plt.subplot(2,2,2)

plt.pcolormesh(x1, x2, area2_predict, cmap=classifier_area_color)                        
plt.scatter(x_train[:,0], x_train[:,1], c=y_train,marker='o', s=50, cmap=cm_dark)    
plt.scatter(x_test[:,0],x_test[:,1], c=y_test,marker='x', s=50, cmap=cm_dark)

plt.xlabel(iris.feature_names[0]+':花萼的长度', fontsize=8)  
plt.ylabel(iris.feature_names[1]+':花萼的宽度', fontsize=8)
plt.xlim(x1_min, x1_max)  
plt.ylim(x2_min, x2_max)
plt.title(u'SVM_SVC_iris:鸢尾花SVM二特征分类(linear核)', fontsize=8)
plt.text(x1_max-1.5, x1_min-0.1, u'$o---train ; x---test$')
plt.grid(True)

#第三个子图采用Linear核
plt.subplot(2,2,3)

plt.pcolormesh(x1, x2, area3_predict, cmap=classifier_area_color)                        
plt.scatter(x_train[:,0], x_train[:,1], c=y_train,marker='o', s=50, cmap=cm_dark)    
plt.scatter(x_test[:,0],x_test[:,1], c=y_test,marker='x', s=50, cmap=cm_dark)

plt.xlabel(iris.feature_names[0]+':花萼的长度', fontsize=8)  
plt.ylabel(iris.feature_names[1]+':花萼的宽度', fontsize=8)
plt.xlim(x1_min, x1_max)  
plt.ylim(x2_min, x2_max)
plt.title(u'SVM_SVC_iris:鸢尾花SVM二特征分类(rbf核gamma=20)', fontsize=8)
plt.text(x1_max-1.5, x1_min-0.1, u'$o---train ; x---test$')
plt.grid(True)

#第四个子图采用Linear核
plt.subplot(2,2,4)

plt.pcolormesh(x1, x2, area4_predict, cmap=classifier_area_color)                        
plt.scatter(x_train[:,0], x_train[:,1], c=y_train,marker='o', s=50, cmap=cm_dark)    
plt.scatter(x_test[:,0],x_test[:,1], c=y_test,marker='x', s=50, cmap=cm_dark)

plt.xlabel(iris.feature_names[0]+':花萼的长度', fontsize=8)  
plt.ylabel(iris.feature_names[1]+':花萼的宽度', fontsize=8)
plt.xlim(x1_min, x1_max)  
plt.ylim(x2_min, x2_max)
plt.title(u'SVM_SVC_iris:鸢尾花SVM二特征分类(rbf核gamma=30)', fontsize=8)
plt.text(x1_max-1.5, x1_min-0.1, u'$o---train ; x---test$')
plt.grid(True)


plt.show()


