import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

#定义神经层
def add_layer(inputs,in_size,out_size,n_layer,activation_function=None):
    layer_name='layer%s'%n_layer
    with tf.name_scope('ayer_name'):                                                       #可视化
        with tf.name_scope('weignts'):
            Weignts=tf.Variable(tf.random_normal([in_size,out_size]),name='W')             #权重
            tf.summary.histogram(layer_name+'/weights',Weignts)                            #为了通过浏览器观察每一神经层的权重
        with tf.name_scope('weignts'):                                                     #可视化
            biases=tf.Variable(tf.zeros([1,out_size])+0.1,name='b')                        #偏移量
            tf.summary.histogram(layer_name+'/biases',biases)
        with tf.name_scope('Input_mut_W_Plus_bia'):                                        #可视化
            Input_mut_W_Plus_bia=tf.matmul(inputs,Weignts)+biases           
            tf.summary.histogram(layer_name+'/Input_mut_W_Plus_bias',Input_mut_W_Plus_bia) #为了通过浏览器观察每一神经层的权重
        if activation_function is None:                            
            outputs=Input_mut_W_Plus_bia                           
        else:                                                    
            outputs=activation_function(Input_mut_W_Plus_bia)                              #激励函数
            tf.summary.histogram(layer_name+'/outputs',outputs)                            #为了通过浏览器观察每一神经层的输出值
        return outputs

#产生数据
x_data = np.linspace(-1,1,300)[: ,np.newaxis]
noise=np.random.normal(0,0.05,x_data.shape)
y_data =np.square(x_data)-0.5+noise



#None就是代表不管多少例子都可以，1可以理解为样本中只有一个特征
with tf.name_scope('inputs'):                           #可视化
    xs=tf.placeholder(tf.float32,[None,1],name='x_input')
    ys=tf.placeholder(tf.float32,[None,1],name='y_input')

#添加神经层
layer1=add_layer(xs ,1,10,1,activation_function=tf.nn.relu)
#添加神经层
prediction=add_layer(layer1,10,1,2,activation_function=None)

with tf.name_scope('loss'):                                                                          #可视化
    loss=tf.reduce_mean(tf.reduce_sum(tf.square(ys-prediction),reduction_indices=[1]),name='myloss') #代价函数
    tf.summary.scalar('loss',loss)                                                                   #为了通过浏览器观察每一神经层的误差(代价函数)
with tf.name_scope('train_ste'):
    train_step=tf.train.GradientDescentOptimizer(0.1).minimize(loss)                                 #优化函数

init=tf.global_variables_initializer()                                                               #初始化所有变量
sess=tf.Session()
merged=tf.summary.merge_all()                                                                        #将所有需要在浏览器中展现的参数合并在一起                                                                    
writer=tf.summary.FileWriter("logs/",sess.graph)                                                     #将需要可视化的东西写到logs文件下
sess.run(init)

#绘图
fig=plt.figure()
ax=fig.add_subplot(1,1,1)
ax.scatter(x_data ,y_data)
plt.ion()
plt.show()

#训练多次
for i in range(1000):
    sess.run(train_step,feed_dict={xs:x_data,ys:y_data})
    if i%50==0:
        try:
            ax.lines.remove(lines[0])
        except Exception:
            pass
        result=sess.run(merged,feed_dict={xs:x_data,ys:y_data})
        #将需要统计的结果加到writer
        writer.add_summary(result,i)
        prediction_value=sess.run(prediction,feed_dict={xs:x_data,ys:y_data})
        lines=ax.plot(x_data,prediction_value,'r-',lw=5)
        plt.pause(0.3)

