from sklearn import datasets
from sklearn.neighbors  import KNeighborsClassifier

iris=datasets.load_iris()

'''
这里是测试iris数据集的代码
print(iris.keys())
print(iris.data)
print(iris.target)
print(iris.data.shape)
print(iris.feature_names)
print(iris.target_names)
'''
#核心代码
knn=KNeighborsClassifier(n_neighbors=6)
knn.fit(iris['data'],iris['target'])

x=[[4.8,2.5,3.4,1.6],[6.3,3.1,3.2,1.8]]
print(x)

#核心代码
prediction=knn.predict(x)

print(prediction)

