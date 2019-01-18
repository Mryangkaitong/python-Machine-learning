
天池上面的ofo比赛https://tianchi.aliyun.com/getStart/information.htm?spm=5176.100067.5678.2.37521db77jhih7&raceId=231593

数据
    本赛题提供用户在2016年1月1日至2016年6月30日之间真实线上线下消费行为，预测用户在2016年7月领取优惠券后15天以内的使用情况。 
注意： 为了保护用户和商家的隐私，所有数据均作匿名处理，同时采用了有偏采样和必要过滤。

评价方式
    本赛题目标是预测投放的优惠券是否核销。针对此任务及一些相关背景知识，使用优惠券核销预测的平均AUC（ROC曲线下面积）作为评价标准。 即对每个优惠券coupon_id单独计算核销预测的AUC值，再对所有优惠券的AUC值求平均作为最终的评价标准。 关于AUC的含义与具体计算方法，可参考维基百科
    
 解题思路来源：https://github.com/wepe/O2O-Coupon-Usage-Forecast
 
 笔者这里进行了总结归纳

DATA/data_origin是原始数据

DATA/data_preprocessed是预处理过的数据

code/ofoFeature.ipynb提取特征即由	data_origin产生data_preprocessed

code/Xgboost.ipynb模型训练

更多解析请看笔者的博客：https://blog.csdn.net/weixin_42001089/article/details/85013073?spm=5176.12282029.0.0.1738311fQ5fMqg
