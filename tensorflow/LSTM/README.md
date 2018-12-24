
需求：故障检测
根据特征预测故障编号


dataSet:

故障编号一共有12种，即0,2,3,613,9,45,657,884,53,886,93,287

特征数目137种

2MWFeatureList.xlsx:特征说明

20003001#2017-03.csv：样本数据集



code:

Preprocess:数据预处理

Model:LSTM模型训练及其测试




部分结果：

神经网络图：

![image](https://github.com/Mryangkaitong/python-Machine-learning/blob/master/tensorflow/LSTM/photo/graph.png)

准确率和损失率：

![image](https://github.com/Mryangkaitong/python-Machine-learning/blob/master/tensorflow/LSTM/photo/train.png)
![image](https://github.com/Mryangkaitong/python-Machine-learning/blob/master/tensorflow/LSTM/photo/test.png)

更多详细解析：https://blog.csdn.net/weixin_42001089/article/details/85231301
