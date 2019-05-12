#加载必要的包
import time
import pandas as pd
import numpy as np
from datetime import date
from sklearn.externals.joblib import Parallel, delayed
import xgboost as xgb
import seaborn as sns
import operator
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.model_selection import StratifiedKFold, KFold, RepeatedKFold
from tqdm import tqdm, tqdm_notebook
tqdm_notebook().pandas()

#时间转化
def convert2time(time_cur,df):
    date_list = time_cur.split('-')
    year,month,day = int(date_list[0]),int(date_list[1]),int(date_list[2])
    time_cur = date(year,month,day)
    train_start = date(int(2019),int(1),int(1))
    train_end = date(int(2019),int(2),int(27))
    test_start = date(int(2019),int(1),int(8))
    test_end = date(int(2019),int(3),int(6))
    if time_cur>=train_start and time_cur<=train_end:
        df['is_train'] = 1
        df['days_train'] = (date(int(2019),int(2),int(28)) - time_cur).days
    else:
        df['is_train'] = 0
        df['days_train'] = -1

    if time_cur>=test_start and time_cur<=test_end:
        df['is_test'] = 1
        df['days_test'] = (date(int(2019),int(3),int(7)) - time_cur).days
    else:
        df['is_test'] = 0
        df['days_test'] = -1
    return df
           
df = pd.read_csv("data/FT_Camp_2/sz_detail.csv")
df = df[['id','rmb_amt','prt_dt']]
df = df.groupby(df.prt_dt)
retlist = Parallel(n_jobs=4)(delayed(convert2time)(name,group) for name, group in tqdm(df))
df = pd.concat(retlist)


#划分训练/测试集
train = df[df['is_train']==1]
train = train.drop(['prt_dt','is_train','is_test','days_test'],axis=1)
train.rename(columns={'days_train':'days'},inplace=True)
test = df[df['is_test']==1]
test = test.drop(['prt_dt','is_test','is_train','days_train'],axis=1)
test.rename(columns={'days_test':'days'},inplace=True)
del df
print(train.head(5))
print(train.shape)
print(test.head(5))
print(test.shape)

#获取客户个人属性以及label,对性别进行one-hot编码({'\\N', 'F', 'M'})
ust_bas_inf = pd.read_csv("data/FT_Camp_2/cust_bas_inf.csv")
train_click = pd.read_csv("data/FT_Camp_2/train.csv")
train_click = pd.merge(train_click,ust_bas_inf,on='id',how='inner')
train_click = train_click.join(pd.get_dummies(train_click.gender))
print(train_click.shape)
print(train_click.head(1))

#将上述信息合并到训练集和测试集
train = pd.merge(train,train_click,on='id',how='inner')

id_no_transaction = list(set(list(train_click['id'].values)).difference(set(list(train['id'].values))))
df_no_transaction = train_click[train_click['id'].isin(id_no_transaction)]
df_no_transaction['rmb_amt'] = 0
df_no_transaction['days'] = 0
train = pd.concat([train,df_no_transaction])
train = train.drop(['gender','aum306'],axis=1)
train.rename(columns={'aum227':'rest_rmb'},inplace=True)
del df_no_transaction
print(train.shape)
print(len(set(list(train['id'].values))))
print(train.head(1))

test =  pd.merge(test,ust_bas_inf,on='id',how='inner')
test = test.join(pd.get_dummies(test.gender))
test = test.drop(['gender','aum227'],axis=1)
test.rename(columns={'aum306':'rest_rmb'},inplace=True)
del ust_bas_inf
del train_click
print(test.shape)
print(test.head(1))

#提取与收出信息相关的特征
def days_rmb_distribute(name,df):
    #dftemp = pd.DataFrame(index=range(df.shape[0]), dtype=np.float64)
    #dftemp = df.loc[[0]]
    
    #支出
    expenditure_list = pd.Series(df[df['rmb_amt']<0]['rmb_amt'].values)
    df.loc[:, 'expenditure_sum'] = expenditure_list.sum()
    df.loc[:, 'expenditure_count'] = expenditure_list.count()
    df.loc[:, 'expenditure_mean'] = expenditure_list.mean() 
    df.loc[:, 'expenditure_std'] = expenditure_list.std() 
    
    #收入
    income_list = pd.Series(df[df['rmb_amt']>0]['rmb_amt'].values)
    df.loc[:, 'income_sum'] = income_list.sum()
    df.loc[:, 'income_count'] = income_list.count()
    df.loc[:, 'income_mean'] = income_list.mean()
    df.loc[:, 'income_std'] = income_list.std() 
    
    #总体情况
    Transaction_list = pd.Series(df['rmb_amt'].values)
    df.loc[:, 'Transaction_min'] = Transaction_list.min()
    df.loc[:, 'Transaction_max'] = Transaction_list.max()
    df.loc[:, 'Transaction_mean'] = Transaction_list.mean()
    df.loc[:, 'Transaction_std'] = Transaction_list.std()
    df.loc[:, 'Transaction_q95'] = np.quantile(Transaction_list, 0.95)
    df.loc[:, 'Transaction_q99'] = np.quantile(Transaction_list, 0.99)
    df.loc[:, 'Transaction_q05'] = np.quantile(Transaction_list, 0.05)
    df.loc[:, 'Transaction_q01'] = np.quantile(Transaction_list, 0.01)
    
    #最后10天的情况
    last_list = pd.Series(df[df['days'].isin([1,2,3,4,5,6,7,8,9,10])]['rmb_amt'].values)
    df.loc[:, 'last_sum'] = last_list.sum()
    df.loc[:, 'last_max'] = last_list.max()
    df.loc[:, 'last_min'] = last_list.min()
    df.loc[:, 'last_mean'] = last_list.mean() 
    df.loc[:, 'last_std'] = last_list.std()
    
    
    #dftemp = dftemp.drop(['rmb_amt','days'],axis=1)
    
    #个人属性
#     df_days_group = df['rmb_amt'].groupby(df['days']).sum()
#     days_rmb_list = np.ones(58)
#     for day in df_days_group.keys():
#         days_rmb_list[int(day)-1] = df_days_group[day]
    #df = pd.concat([df,dftemp],axis=1)
    df = df.drop(['rmb_amt','days'],axis=1)
    df = df.drop_duplicates(['id'])
    return df

 

train = train.groupby(['id'])
retlist = Parallel(n_jobs=5)(delayed(days_rmb_distribute)(name,group) for name, group in tqdm(train))
train = pd.concat(retlist)
train = train.drop_duplicates(['id'])
del retlist

test = test.groupby(['id'])
retlist = Parallel(n_jobs=5)(delayed(days_rmb_distribute)(name,group) for name, group in tqdm(test))
test = pd.concat(retlist)
test = test.drop_duplicates(['id'])
del retlist

print(train.shape)
print(test.shape)
print(train.head(1))

#制作完整的测试集
ust_bas_inf = pd.read_csv("data/FT_Camp_2/cust_bas_inf.csv")
submission = pd.read_csv('data/FT_Camp_2/pred_users.csv')
print(submission.shape)
testtemp = pd.merge(submission,test,on='id',how='inner')
id_no_transaction = list(set(list(submission['id'].values)).difference(set(list(testtemp['id'].values))))
df_no_transaction = submission[submission['id'].isin(id_no_transaction)]
df_no_transaction = pd.merge(df_no_transaction,ust_bas_inf,on='id',how='inner')
df_no_transaction = df_no_transaction.join(pd.get_dummies(df_no_transaction.gender))
df_no_transaction = df_no_transaction.drop(['gender','aum227'],axis=1)
df_no_transaction.rename(columns={'aum306':'rest_rmb'},inplace=True)
testtemp = pd.concat([df_no_transaction,testtemp])
testtemp = testtemp.fillna(0)
print(testtemp.shape)
print(testtemp.head(4))

#去除非法字符串\\N
feature_name = test.columns.tolist()
feature_name.remove('id')
train_y = train['click_w228']
train_x = train[feature_name]
train_x = train_x.replace('\\N',0)
test_x = testtemp[feature_name]
test_x = test_x.replace('\\N',0)
print(train_x.shape)
print(test_x.shape)
print(train_x.head(1))

#训练模型
n_fold = 5
folds = KFold(n_splits=n_fold, shuffle=True)

def train_model(X=train_x.values ,y=train_y.values,featurename=feature_name, X_test=test_x.values, params=None, folds=folds, model_type='lgb', plot_feature_importance=False, model=None):
    oof = np.zeros(len(X))
    prediction = np.zeros(len(X_test))
    scores = []
    feature_importance = pd.DataFrame()
    for fold_n, (train_index, valid_index) in enumerate(folds.split(X)):
        print('Fold', fold_n, 'started at', time.ctime())
        X_train, X_valid = X[train_index], X[valid_index]
        y_train, y_valid = y[train_index], y[valid_index]
        if model_type == 'lgb':
            train_data = lgb.Dataset(data=X_train, label=y_train)
            valid_data = lgb.Dataset(data=X_valid, label=y_valid)
            model = lgb.train(params,train_data,num_boost_round=20000,
                    valid_sets = [train_data, valid_data],verbose_eval=1000,early_stopping_rounds = 200)
            
            y_pred_valid = model.predict(X_valid)
            y_pred = model.predict(X_test, num_iteration=model.best_iteration)
            
        if model_type == 'xgb':
            train_data = xgb.DMatrix(data=X_train, label=y_train, feature_names=featurename)
            valid_data = xgb.DMatrix(data=X_valid, label=y_valid, feature_names=featurename)
            watchlist = [(train_data, 'train'), (valid_data, 'valid_data')]
            model = xgb.train(dtrain=train_data, num_boost_round=15000, evals=watchlist, early_stopping_rounds=200, verbose_eval=1000, params=params)
            y_pred_valid = model.predict(xgb.DMatrix(X_valid, feature_names=featurename), ntree_limit=model.best_ntree_limit)
            y_pred = model.predict(xgb.DMatrix(X_test, feature_names=featurename), ntree_limit=model.best_ntree_limit)
            
        if model_type == 'rcv':
            model = RidgeCV(alphas=(0.01, 0.1, 1.0, 10.0, 100.0), scoring='neg_mean_absolute_error', cv=3)
            model.fit(X_train, y_train)
            print(model.alpha_)

            y_pred_valid = model.predict(X_valid).reshape(-1,)
            score = mean_absolute_error(y_valid, y_pred_valid)
            print(f'Fold {fold_n}. MAE: {score:.4f}.')
            print('')
            y_pred = model.predict(X_test).reshape(-1,)
        
        if model_type == 'sklearn':
            model = model
            model.fit(X_train, y_train)
            
            y_pred_valid = model.predict(X_valid).reshape(-1,)
            score = mean_absolute_error(y_valid, y_pred_valid)
            print(f'Fold {fold_n}. MAE: {score:.4f}.')
            print('')
            
            y_pred = model.predict(X_test).reshape(-1,)
        
        if model_type == 'cat':
            model = CatBoostRegressor(iterations=20000,  eval_metric='auc', **params)
            model.fit(X_train, y_train, eval_set=(X_valid, y_valid), cat_features=[], use_best_model=True, verbose=False)
            y_pred_valid = model.predict(X_valid)
            y_pred = model.predict(X_test)
        
        oof[valid_index] = y_pred_valid.reshape(-1,)
        fpr, tpr, thresholds = metrics.roc_curve(y_valid, y_pred_valid, pos_label=1)
        scores.append(metrics.auc(fpr, tpr))

        prediction += y_pred    
        
        if model_type == 'lgb':
            # feature importance
            fold_importance = pd.DataFrame()
            fold_importance["feature"] = featurename
            fold_importance["importance"] = model.feature_importance()
            fold_importance["fold"] = fold_n + 1
            feature_importance = pd.concat([feature_importance, fold_importance], axis=0)
        if model_type == 'xgb':
            fold_importance =  model.get_fscore() 
            fold_importance = sorted(fold_importance.items(), key=operator.itemgetter(1))  
            feature_importance = pd.DataFrame(fold_importance, columns=['feature', 'importance'])           
    prediction /= n_fold
    print('CV mean score: {0:.4f}, std: {1:.4f}.'.format(np.mean(scores), np.std(scores)))
    
    if model_type == 'lgb':
        feature_importance["importance"] /= n_fold
        if plot_feature_importance:
            cols = feature_importance[["feature", "importance"]].groupby("feature").mean().sort_values(
                by="importance", ascending=False)[:25].index

            best_features = feature_importance.loc[feature_importance.feature.isin(cols)]

            plt.figure(figsize=(16,26))
            sns.barplot(x="importance", y="feature", data=best_features.sort_values(by="importance", ascending=False))
            plt.title('LGB Features (avg over folds)')
        
            return oof, prediction, feature_importance
        return oof, prediction
    
    elif model_type == 'xgb':
        feature_importance['importance'] /= n_fold
        if plot_feature_importance:
            plt.figure(figsize=(16,26))  
            feature_importance.plot(kind='barh', x='feature', y='importance', legend=False, figsize=(6, 10))  
            plt.title('XGB Features (avg over folds)')  
            plt.xlabel('relative importance')  
            plt.show() 
            return oof, prediction, feature_importance
        return oof, prediction
    else:
        return oof, prediction
		
%%time
%%time
params = {'eta':0.05,
          'max_depth':4,  
          'subsample':0.5,
          'colsample_bytree':0.5,
          'alpha':0.1,
          'nthread':7,
          'min_samples_split':10,
          'min_samples_leaf':10,
          'max_leaf_nodes':10,
          'objective':'binary:logistic',
          'random_state':42,
          'eval_metric' : "auc",
          'booster' : "gbtree"}

oof_xgb, prediction_xgb = train_model(params=params, model_type='xgb',plot_feature_importance=True)
testtemp['score'] = prediction_xgb

#保存查看结果
testtemp = testtemp[['id','score']]
testtemp.to_csv("result.csv")
print(testtemp.shape)
print(testtemp.head(5))

#提交结果
import xlab
xlab.ftcamp.submit("result.csv")