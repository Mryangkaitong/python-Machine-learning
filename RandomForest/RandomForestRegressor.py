#随机森林回归
import matplotlib as mpl
import numpy as np
import warnings 
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor

#忽略一些版本不兼容等警告
warnings.filterwarnings("ignore")

#产生心状坐标
t = np.arange(0,2*np.pi,0.1)
x = 16*np.sin(t)**3
x=x[:, np.newaxis]
y = 13*np.cos(t)-5*np.cos(2*t)-2*np.cos(3*t)-np.cos(4*t)
y[::7]+= 3* (1 - np.random.rand(9))                      #增加噪声，在每数2个数的时候增加一点噪声

#传统决策树线性回归,随机森林回归，极端森林回归
rf1=DecisionTreeRegressor()
rf2=RandomForestRegressor(n_estimators=1000)
rf3=ExtraTreesRegressor()


#三种算法的预测
y_rf1 =rf1.fit(x,y).predict(x)
y_rf2 =rf2.fit(x,y).predict(x)
y_rf3 =rf3.fit(x,y).predict(x)

#为了后面plt.text定位
x1_min, x1_max = x[:].min(), x[:].max()          
x2_min, x2_max = y[:].min(), y[:].max()

mpl.rcParams['font.sans-serif'] = [u'SimHei']            #用来正常显示中文标签    
mpl.rcParams['axes.unicode_minus'] = False

plt.scatter(x, y, color='darkorange', label='data')  
plt.hold('on')

plt.plot(x, y_rf1, color='b',  label='DecisionTreeRegressor')  
plt.plot(x, y_rf2, color='g',  label='RandomForestRegressor')  
plt.plot(x, y_rf3, color='r',  label='ExtraTreesRegressor')

plt.xlabel('data_x')  
plt.ylabel('data_y')  
plt.title('python_machine-learning_RandomForest(n_estimators=1000)-----心状学习')  
plt.legend()
plt.text(x1_max-4, x2_max-1, u'$o---Sample-Point$')
plt.show()

