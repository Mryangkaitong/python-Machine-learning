#tensorflow分类
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

#产生数据
mnist=input_data.read_data_sets('.',one_hot=True)     #如果没有这个包它会自动下载

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

#定义准确率:tensorflow定义完了都是要有sess.run来运行的
def compute_accuracy(v_xs,v_ys):
    global prediction                                     #prediction全局化
    y_pre=sess.run(prediction,feed_dict={xs:v_xs})         #预测值
    correct_prediction=tf.equal(tf.argmax(y_pre,1),tf.argmax(v_ys,1))
    accuracy=tf.reduce_mean(tf.cast( correct_prediction,tf.float32))
    result=sess.run(accuracy,feed_dict={xs:v_xs,ys:v_ys})          #运行上面定义的accuracy
    return result 
    
#定义给输入定义placeholder
#None就是代表不管多少例子都可以，784可以理解为样本中只有一个特征
with tf.name_scope('inputs'):                                   #可视化
    xs=tf.placeholder(tf.float32,[None,784],name='x_input')    #28*28 
    ys=tf.placeholder(tf.float32,[None,10],name='y_input')

#核心：添加神经层tf.nn.softmax一般用来分类
prediction=add_layer(xs,784,10,1,activation_function=tf.nn.softmax)
#核心：cross_entropy的构建
with tf.name_scope('cross_entropy'):                                                                          #可视化
    cross_entropy=tf.reduce_mean(-tf.reduce_sum(ys*tf.log(prediction),reduction_indices=[1]))              #代价函数,分类用softma和coss_entropy配
    tf.summary.scalar('cross_entropy',cross_entropy)                                                      #为了通过浏览器观察每一神经层的误差(代价函数)
with tf.name_scope('train_ste'):
    train_step=tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)                                 #优化函数

init=tf.global_variables_initializer()                                                               #初始化所有变量
sess=tf.Session()
merged=tf.summary.merge_all()                                                                        #将所有需要在浏览器中展现的参数合并在一起                                                                    
writer=tf.summary.FileWriter("logs/",sess.graph)                                                     #将需要可视化的东西写到logs文件下
sess.run(init)


#训练多次
for i in range(1000):
    batch_xs,batch_ys=mnist.train.next_batch(100)
    sess.run(train_step,feed_dict={xs:batch_xs,ys:batch_ys})
    if i%50==0:
        result=sess.run(merged,feed_dict={xs:batch_xs,ys:batch_ys})
        #将需要统计的结果加到writer
        writer.add_summary(result,i)
        print(compute_accuracy(mnist.test.images,mnist.test.labels))  #打印准确度
        
      

