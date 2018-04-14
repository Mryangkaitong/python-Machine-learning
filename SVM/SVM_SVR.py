#SVM回归
import matplotlib as mpl
import numpy as np
import warnings
from sklearn.svm import SVR  
import matplotlib.pyplot as plt

#忽略一些版本不兼容等警告
warnings.filterwarnings("ignore")

#产生心状坐标
t = np.arange(0,2*np.pi,0.1)
x = 16*np.sin(t)**3
x=x[:, np.newaxis]
y = 13*np.cos(t)-5*np.cos(2*t)-2*np.cos(3*t)-np.cos(4*t)
y[::7]+= 2* (1 - np.random.rand(9))                     #增加噪声，在每数2个数的时候增加一点噪声



svr_rbf=SVR(kernel='rbf', C=1e3, gamma=200)      
svr_lin = SVR(kernel='linear', C=1500)  
svr_poly = SVR(kernel='poly', C=1500, degree=2)

#三种核函数预测
y_rbf = svr_rbf.fit(x,y).predict(x)
y_lin = svr_lin.fit(x,y).predict(x)
y_poly = svr_poly.fit(x,y).predict(x)

#为了后面plt.text定位
x1_min, x1_max = x[:].min(), x[:].max()          
x2_min, x2_max = y[:].min(), y[:].max()


mpl.rcParams['font.sans-serif'] = [u'SimHei']            #用来正常显示中文标签    
mpl.rcParams['axes.unicode_minus'] = False

plt.scatter(x, y, color='darkorange', label='data')  
plt.hold('on')

plt.plot(x, y_rbf, color='r',  label='RBF model')  
plt.plot(x, y_lin, color='g',  label='Linear model')  
plt.plot(x, y_poly, color='b', label='Polynomial model')

plt.xlabel('data')  
plt.ylabel('target')  
plt.title('python_machine-learning_svm-svr-----心状学习')  
plt.legend()
plt.text(x1_max-4, x2_max-1, u'$o---Sample-Point$')
plt.show()



