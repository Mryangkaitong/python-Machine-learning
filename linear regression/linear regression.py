from sklearn import datasets,linear_model
import matplotlib.pyplot as plt
import numpy as np

diabetes=datasets.load_diabetes()
diabetes_x=diabetes.data[:,np.newaxis ,3]#取第四列数据

diabetes_x_train=diabetes_x[:-20]
diabetes_x_test=diabetes_x[-20:]

diabetes_y_train=diabetes.target[:-20]
diabetes_y_test=diabetes.target[-20:]

#核心代码
regr=linear_model.LinearRegression()
regr.fit(diabetes_x_train,diabetes_y_train)

print('Input Values')
print(diabetes_x_test)

#核心代码
diabetes_y_pred=regr.predict(diabetes_x_test)
print('Predicted Output Values')
print(diabetes_y_pred)

plt.scatter(diabetes_x_test,diabetes_y_test,color='black')
plt.plot(diabetes_x_test,diabetes_y_pred,color='red',linewidth=1)
plt.show()
