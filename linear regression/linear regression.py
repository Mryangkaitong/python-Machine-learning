#LinearRegression线性回归
from sklearn import datasets,linear_model
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

diabetes=datasets.load_diabetes()
diabetes_x=diabetes.data[:,np.newaxis ,2]               #取第三列数据

diabetes_x_train=diabetes_x[:-20]
diabetes_x_test=diabetes_x[-20:]

diabetes_y_train=diabetes.target[:-20]
diabetes_y_test=diabetes.target[-20:]

#核心代码
regr=linear_model.LinearRegression()
regr.fit(diabetes_x_train,diabetes_y_train)             #用训练集进行训练模型

print('Input Values')
print(diabetes_x_test)

#核心代码
diabetes_y_pred=regr.predict(diabetes_x_test)
print('Predicted Output Values')
print(diabetes_y_pred)

#绘图
mpl.rcParams['font.sans-serif'] = [u'SimHei']            #用来正常显示中文标签    
mpl.rcParams['axes.unicode_minus'] = False               #用来正常显示负号

plt.scatter(diabetes_x_test,diabetes_y_test,color='black')
plt.plot(diabetes_x_test,diabetes_y_pred,color='red',linewidth=1)

plt.xlabel('体质指数', fontsize=12)  
plt.ylabel('一年后患疾病的定量指标', fontsize=12)
plt.title(u'LinearRegression线性回归', fontsize=12)

plt.show()
