#PCA
import warnings
from sklearn import metrics 
from sklearn.cross_validation import train_test_split
from sklearn.datasets import fetch_lfw_people
from sklearn.decomposition import PCA
from sklearn.neighbors  import KNeighborsClassifier  

#忽略一些版本不兼容等警告
warnings.filterwarnings("ignore")

lfw_people = fetch_lfw_people(min_faces_per_person=70, resize=0.4)

x=lfw_people.data
n_features=x.shape[1]
y=lfw_people.target
target_names=lfw_people.target_names

#分割训练集和测试集
x_train,x_test,y_train,y_test = train_test_split(x, y, test_size=0.4)
#先训练PCA模型
PCA=PCA(n_components=100).fit(x_train)
#返回测试集和训练集降维后的数据集
x_train_pca = PCA.transform(x_train)
x_test_pca = PCA.transform(x_test)

#KNN核心代码  
knn=KNeighborsClassifier(n_neighbors=6)  
knn.fit(x_train_pca ,y_train)                      #用训练集进行训练模型  

#识别测试集中的人脸
y_test_predict=knn.predict(x_test_pca)

'''
#输出
for i in range(len(y_test_predict)):
    print(target_names[y_test_predict[i]])
    
'''


print(knn.score(x_test_pca, y_test))                        #预测准确率  
print(metrics.classification_report(y_test,y_test_predict)) #包含准确率，召回率等信息表  
print(metrics.confusion_matrix(y_test,y_test_predict))      #混淆矩阵
