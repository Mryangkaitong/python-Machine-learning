# -*- coding: utf-8 -*
import pandas as pd
import numpy as np
import xgboost as xgb
from collections import Counter
import lightgbm as lgb
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
import copy
from sklearn.preprocessing import MinMaxScaler
import collections
import operator
import time
from sklearn.decomposition import PCA
import scipy.stats as sp
import warnings
from sklearn import metrics
from sklearn.model_selection import StratifiedKFold, KFold, RepeatedKFold
warnings.filterwarnings('ignore')


train_beh = pd.read_csv("./data/train/train_beh.csv")
train_tag = pd.read_csv("./data/train/train_tag.csv")
train_trd = pd.read_csv("./data/train/train_trd.csv")

test_beh = pd.read_csv("./data/test/test_beh.csv")
test_tag = pd.read_csv("./data/test/test_tag.csv")
test_trd = pd.read_csv("./data/test/test_trd.csv")

test_beh.rename(columns = {"Unnamed: 2": "Unnamed: 3"},inplace=True)
train_tag['train_flag'] = 0
test_tag['train_flag'] = 1

data_beh = train_beh.append(test_beh)
data_tag = train_tag.append(test_tag)
data_trd = train_trd.append(test_trd)


def get_month(month):
    if month=='5':
        return 0
    else:
        return 1


def get_week(day):
    day = int(day)
    pre_week = 0
    if day > 30:
        pre_week = 5
        day = day - 30

    if day >= 1 and day <= 7:
        return 1 + pre_week
    if day >= 8  and  day <= 14:
        return 2 + pre_week
    if day >= 15 and day <= 21:
        return 3 + pre_week
    if day >= 22 and day <= 28:
        return 4 + pre_week
    if day >= 28:
        return 5 + pre_week


def get_day(month_day):
    month = month_day[6:7]
    day = month_day[8:10]
    day = int(day)
    if month == '5':
        return 30 + day
    else:
        return day


def get_time_gap(strs,parm):
    time = strs.split(":")
    time = list(set(time))
    time = sorted(list(map(lambda x:int(x),time)))
    time_gap = []
    #用户只在当天活跃
    if len(time) == 1:
        return -30

    for index, value in enumerate(time):
        if index <= len(time) - 2:
            gap = abs(time[index] - time[index + 1])
            time_gap.append(gap)

    if parm == '1':
        return np.mean(time_gap)
    elif parm == '2':
        return np.max(time_gap)
    elif parm == '3':
        return np.min(time_gap)
    elif parm == '4':
        return np.std(time_gap)
    elif parm == '5':
        return sp.stats.skew(time_gap)
    elif parm == '6':
        return sp.stats.kurtosis(time_gap)


def get_tag_feature(temp):
    def trans_category(data, feature_name, fill_style='nan'):
        if fill_style=='nan':
            for name in feature_name:
                data[name] = data[name].apply(lambda x: int(x) if x!='\\N' else np.nan)
        elif fill_style=='zero':
            for name in feature_name:
                data[name] = data[name].apply(lambda x: int(x) if x != '\\N' else 0)
        else:
            for name in feature_name:
                data[name] = data[name].astype('category').cat.codes
        return data
    def get_gdr_cd_category(x):
        if x=='M':
            return 0
        elif x=='F':
            return 1
        else:
            return np.nan
    def get_mrg_situ_cd_category(x):
        if x=='A':
            return 0
        elif x=='B':
            return 1
        elif x=='O':
            return 2
        elif x=='Z':
            return 3
        else:
            return np.nan
    def get_edu_deg_cd_category(x):
        if x=='G':
            return 0
        elif x=='A':
            return 1
        elif x=='F':
            return 2
        elif x=='Z':
            return 3
        elif x=='D':
            return 4
        elif x=='M':
            return 5
        elif x=='B':
            return 6
        elif x=='J':
            return 7
        elif x=='K':
            return 8
        elif x=='C':
            return 9
        elif x=='L':
            return 10
        else:
            return np.nan

    def get_acdm_deg_cd_category(x):
        if x=='G':
            return 0
        elif x=='F':
            return 1
        elif x=='Z':
            return 2
        elif x=='D':
            return 3
        elif x=='30':
            return 4
        elif x=='31':
            return 5
        elif x=='C':
            return 6
        else:
            return np.nan

    def get_deg_cd_category(x):
        if x=='A':
            return 0
        elif x=='Z':
            return 1
        elif x=='D':
            return 2
        elif x=='B':
            return 3
        elif x=='C':
            return 4
        else:
            return np.nan

    def get_two_category(x):
        if x=='1':
            return 1
        elif x=='0':
            return 0
        else:
            return np.nan
    temp['gdr_cd'] = temp.gdr_cd.apply(get_gdr_cd_category)
    #temp['age'] = pd.cut(temp['age'], [18,29,39,49,59,84], labels=False).astype('category').cat.codes
    temp['mrg_situ_cd'] = temp.mrg_situ_cd.apply(get_mrg_situ_cd_category)
    temp['edu_deg_cd'] = temp.edu_deg_cd.apply(get_edu_deg_cd_category)
    temp['acdm_deg_cd'] = temp.acdm_deg_cd.apply(get_acdm_deg_cd_category)
    temp['deg_cd'] = temp.deg_cd.apply(get_deg_cd_category)
    #temp['job_year'] = pd.cut(temp['job_year'], [0, 5, 10, 30, 50, 70,99], labels=False).astype('category').cat.codes
    #temp['l6mon_daim_aum_cd'] = temp.l6mon_daim_aum_cd.apply(lambda x: int(x) if x==-1 else np.nan)
    #bk1_cur_year_mon_avg_agn_amt_cd
    #pl_crd_lmt_cd
    category_feature_name_zero = ['his_lng_ovd_day', 'ovd_30d_loan_tot_cnt','l12_mon_gld_buy_whl_tms','l12_mon_insu_buy_whl_tms',
                                  'l12_mon_fnd_buy_whl_tms', 'l12mon_buy_fin_mng_whl_tms']
    category_feature_name_nan = ['crd_card_act_ind', 'l1y_crd_card_csm_amt_dlm_cd','hld_crd_card_grd_cd',
                                 'loan_act_ind','pot_ast_lvl_cd','tot_ast_lvl_cd','cust_inv_rsk_endu_lvl_cd',
                                 'confirm_rsk_ases_lvl_typ_cd','fin_rsk_ases_grd_cd','vld_rsk_ases_ind',
                                 'frs_agn_dt_cnt','l6mon_agn_ind','hav_hou_grp_ind','hav_car_grp_ind',
                                 'dnl_bind_cmb_lif_ind','dnl_mbl_bnk_ind','fr_or_sh_ind','ic_ind', 'job_year']
    category_feature_name_no_fill = ['cur_debit_crd_lvl']
    temp = trans_category(temp, category_feature_name_nan, fill_style='nan')
    temp = trans_category(temp, category_feature_name_zero, fill_style='zero')
    temp = trans_category(temp, category_feature_name_no_fill, fill_style='no_fill')
    temp['atdd_type'] = temp.atdd_type.apply(lambda x: int(x) if (x=='1' or x=='0' or x==0 or x==1) else np.nan)
    #perm_crd_lmt_cd
    #cur_debit_cnt
    #cur_credit_cnt
    temp['cur_debit_min_opn_dt_cnt'] = temp.cur_debit_min_opn_dt_cnt.apply(lambda x:int(x) if x!=-1 else 0)
    temp['cur_credit_min_opn_dt_cnt'] = temp.cur_credit_min_opn_dt_cnt.apply(lambda x:int(x) if x!=-1 else 0)
    #理财产品，基金，保险，黄金占比
    temp_name = ['l12mon_buy_fin_mng_whl_tms','l12_mon_fnd_buy_whl_tms','l12_mon_insu_buy_whl_tms', 'l12_mon_gld_buy_whl_tms']
    temp['all_buy_count'] = temp['l12mon_buy_fin_mng_whl_tms'] + temp['l12_mon_fnd_buy_whl_tms'] + temp['l12_mon_insu_buy_whl_tms'] +temp['l12_mon_gld_buy_whl_tms']
    temp['all_buy_count_temp'] = temp['all_buy_count'].apply(lambda x:x if x!=0 else 0.1)
    for name in temp_name:
        new_name = name + '_ratio'
        temp[new_name] = temp[name] / temp['all_buy_count_temp']
    #平均每卡持有天数
    temp['debit_temp'] = temp['cur_debit_cnt'].apply(lambda x:x if x!=0 else 0.1)
    temp['credit_temp'] = temp['cur_credit_cnt'].apply(lambda x:x if x!=0 else 0.1)
    temp['debit/cnt'] = temp['cur_debit_min_opn_dt_cnt']/temp['debit_temp']
    temp['credit/cnt'] = temp['cur_credit_min_opn_dt_cnt']/temp['credit_temp']
    temp = temp.drop(['debit_temp','credit_temp', 'all_buy_count_temp'],axis=1)
    return temp


def cur_day_repeat_count(strs):
    time = strs.split(":")
    time = dict(Counter(time))
    time = sorted(time.items(), key=lambda x: x[1], reverse=False)
    # 一天一次启动
    if (len(time) == 1) & (time[0][1] == 1):
        return 0
    # 一天多次启动
    elif (len(time) == 1) & (time[0][1] > 1):
        return 1
    # 多天多次启动
    elif (len(time) > 1) & (time[0][1] >= 2):
        return 2
    else:
        return 3


def get_continue_launch_count(strs,parm):
    time = strs.split(":")
    time = dict(Counter(time))
    time = sorted(time.items(), key=lambda x: x[0], reverse=False)
    key_list = []
    value_list = []
    if len(time) == 1:
        return -2
    for key,value in dict(time).items():
        key_list.append(int(key))
        value_list.append(int(value))

    if np.mean(np.diff(key_list, 1)) == 1:
        if parm == '1':
            return np.mean(value_list)
        elif parm == '2':
            return np.max(value_list)
        elif parm == '3':
            return np.min(value_list)
        elif parm == '4':
            return np.sum(value_list)
        elif parm == '5':
            return np.std(value_list)
    else:
        return -1


def get_lianxu_day(day_list):
    time = day_list.split(":")
    time = list(map(lambda x:int(x),time))
    m = np.array(time)
    if len(set(m)) == 1:
        return -1
    m = list(set(m))
    if len(m) == 0:
        return -20
    n = np.where(np.diff(m) == 1)[0]
    i = 0
    result = []
    while i < len(n) - 1:
        state = 1
        while n[i + 1] - n[i] == 1:
            state += 1
            i += 1
            if i == len(n) - 1:
                break
        if state == 1:
            i += 1
            result.append(2)
        else:
            i += 1
            result.append(state + 1)
    if len(n) == 1:
        result.append(2)
    if len(result) != 0:
        # print(result)
        return np.max(result)


def get_time_feature(data, return_data, time_name='trx_tm', catgory_name='Trx_Cod1_Cd', phase=''):
    # 天数
    data['month'] = data[time_name].apply(lambda x: int(x[6:7]))
    data['month'] = data['month'].apply(get_month)
    data['day'] = data[time_name].apply(get_day)
    data['hour'] = data[time_name].apply(lambda x: int(x[11:13]))
    data['week'] = data['day'].apply(get_week)

    feat = data[['id', 'day']]
    feat[phase + 'day'] = feat['day'].astype('str')
    feat = feat.groupby(['id'])[phase + 'day'].agg(lambda x: ':'.join(x)).reset_index()
    feat.rename(columns={phase + 'day': 'act_list'}, inplace=True)
    # 用户是否多天有多次交易
    feat[phase + 'time_gap_mean'] = feat['act_list'].apply(get_time_gap, args=('1'))
    feat[phase + 'time_gap_max'] = feat['act_list'].apply(get_time_gap, args=('2'))
    feat[phase + 'time_gap_min'] = feat['act_list'].apply(get_time_gap, args=('3'))
    feat[phase + 'time_gap_std'] = feat['act_list'].apply(get_time_gap, args=('4'))
    feat[phase + 'time_gap_skew'] = feat['act_list'].apply(get_time_gap, args=('5'))
    feat[phase + 'time_gap_kurt'] = feat['act_list'].apply(get_time_gap, args=('6'))
    # 平均行为次数
    feat[phase + 'mean_act_count'] = feat['act_list'].apply(lambda x: len(x.split(":")) / len(set(x.split(":"))))
    # 平均行为日期
    feat[phase + 'act_mean_date'] = feat['act_list'].apply(lambda x: np.sum([int(ele) for ele in x.split(":")]) / len(x.split(":")))
    # 用户是否当天有多次启动
    feat[phase + 'cur_day_repeat_count'] = feat['act_list'].apply(cur_day_repeat_count)
    # 连续几天启动次数的均值，
    feat[phase + 'con_act_day_count_mean'] = feat['act_list'].apply(get_continue_launch_count, args=('1'))
    # 最大值，
    feat[phase + 'con_act_day_count_max'] = feat['act_list'].apply(get_continue_launch_count, args=('2'))
    # 最小值
    feat[phase + 'con_act_day_count_min'] = feat['act_list'].apply(get_continue_launch_count, args=('3'))
    # 次数
    feat[phase + 'con_act_day_count_total'] = feat['act_list'].apply(get_continue_launch_count, args=('4'))
    # 方差
    feat[phase + 'con_act_day_count_std'] = feat['act_list'].apply(get_continue_launch_count, args=('5'))
    feat[phase + 'con_act_max'] = feat['act_list'].apply(get_lianxu_day)
    del feat['act_list']
    return_data = pd.merge(return_data, feat, on=['id'], how='left')

    temp_name = catgory_name + 'count'
    feat = data.groupby(['id', 'day'], as_index=False)[catgory_name].agg({temp_name: "count"})
    feat_copy = feat.copy()
    for i in ['mean', 'max', 'min', 'std', 'median']:
        col = temp_name + "_" + i
        feat = feat_copy.groupby(['id'], as_index=False)[temp_name].agg({col: i})
        return_data = pd.merge(return_data, feat, on=['id'], how='left')
    # 用户每天启动次数的众值
    feat = feat_copy.groupby(['id'], as_index=False)[temp_name].agg({temp_name + "_mode_count": lambda x: x.value_counts().index[0]})
    return_data = pd.merge(return_data, feat, on=['id'], how='left')
    # 峰度
    feat = feat_copy.groupby(['id'], as_index=False)[temp_name].agg({temp_name + "_skew_count": sp.stats.skew})
    return_data = pd.merge(return_data, feat, on=['id'], how='left')
    # 偏度
    feat = feat_copy.groupby(['id'], as_index=False)[temp_name].agg({temp_name+"_kurt_count": sp.stats.kurtosis})
    return_data = pd.merge(return_data, feat, on=['id'], how='left')

    return return_data


def get_tag_feature(temp):
    def trans_category(data, feature_name, fill_style='nan'):
        if fill_style=='nan':
            for name in feature_name:
                data[name] = data[name].apply(lambda x: int(x) if x!='\\N' else np.nan)
        elif fill_style=='zero':
            for name in feature_name:
                data[name] = data[name].apply(lambda x: int(x) if x != '\\N' else 0)
        else:
            for name in feature_name:
                data[name] = data[name].astype('category').cat.codes
        return data
    def get_gdr_cd_category(x):
        if x=='M':
            return 0
        elif x=='F':
            return 1
        else:
            return np.nan
    def get_mrg_situ_cd_category(x):
        if x=='A':
            return 0
        elif x=='B':
            return 1
        elif x=='O':
            return 2
        elif x=='Z':
            return 3
        else:
            return np.nan
    def get_edu_deg_cd_category(x):
        if x=='G':
            return 0
        elif x=='A':
            return 1
        elif x=='F':
            return 2
        elif x=='Z':
            return 3
        elif x=='D':
            return 4
        elif x=='M':
            return 5
        elif x=='B':
            return 6
        elif x=='J':
            return 7
        elif x=='K':
            return 8
        elif x=='C':
            return 9
        elif x=='L':
            return 10
        else:
            return np.nan

    def get_acdm_deg_cd_category(x):
        if x=='G':
            return 0
        elif x=='F':
            return 1
        elif x=='Z':
            return 2
        elif x=='D':
            return 3
        elif x=='30':
            return 4
        elif x=='31':
            return 5
        elif x=='C':
            return 6
        else:
            return np.nan

    def get_deg_cd_category(x):
        if x=='A':
            return 0
        elif x=='Z':
            return 1
        elif x=='D':
            return 2
        elif x=='B':
            return 3
        elif x=='C':
            return 4
        else:
            return np.nan

    def get_two_category(x):
        if x=='1':
            return 1
        elif x=='0':
            return 0
        else:
            return np.nan
    temp['gdr_cd'] = temp.gdr_cd.apply(get_gdr_cd_category)
    #temp['age'] = pd.cut(temp['age'], [18,29,39,49,59,84], labels=False).astype('category').cat.codes
    temp['mrg_situ_cd'] = temp.mrg_situ_cd.apply(get_mrg_situ_cd_category)
    temp['edu_deg_cd'] = temp.edu_deg_cd.apply(get_edu_deg_cd_category)
    temp['acdm_deg_cd'] = temp.acdm_deg_cd.apply(get_acdm_deg_cd_category)
    temp['deg_cd'] = temp.deg_cd.apply(get_deg_cd_category)
    #temp['job_year'] = pd.cut(temp['job_year'], [0, 5, 10, 30, 50, 70,99], labels=False).astype('category').cat.codes
    #temp['l6mon_daim_aum_cd'] = temp.l6mon_daim_aum_cd.apply(lambda x: int(x) if x==-1 else np.nan)
    #bk1_cur_year_mon_avg_agn_amt_cd
    #pl_crd_lmt_cd
    category_feature_name_zero = ['his_lng_ovd_day', 'ovd_30d_loan_tot_cnt','l12_mon_gld_buy_whl_tms','l12_mon_insu_buy_whl_tms',
                                  'l12_mon_fnd_buy_whl_tms', 'l12mon_buy_fin_mng_whl_tms']
    category_feature_name_nan = ['crd_card_act_ind', 'l1y_crd_card_csm_amt_dlm_cd','hld_crd_card_grd_cd',
                                 'loan_act_ind','pot_ast_lvl_cd','tot_ast_lvl_cd','cust_inv_rsk_endu_lvl_cd',
                                 'confirm_rsk_ases_lvl_typ_cd','fin_rsk_ases_grd_cd','vld_rsk_ases_ind',
                                 'frs_agn_dt_cnt','l6mon_agn_ind','hav_hou_grp_ind','hav_car_grp_ind',
                                 'dnl_bind_cmb_lif_ind','dnl_mbl_bnk_ind','fr_or_sh_ind','ic_ind', 'job_year']
    category_feature_name_no_fill = ['cur_debit_crd_lvl']
    temp = trans_category(temp, category_feature_name_nan, fill_style='nan')
    temp = trans_category(temp, category_feature_name_zero, fill_style='zero')
    temp = trans_category(temp, category_feature_name_no_fill, fill_style='no_fill')
    temp['atdd_type'] = temp.atdd_type.apply(lambda x: int(x) if (x=='1' or x=='0' or x==0 or x==1) else np.nan)
    #perm_crd_lmt_cd
    #cur_debit_cnt
    #cur_credit_cnt
    temp['cur_debit_min_opn_dt_cnt'] = temp.cur_debit_min_opn_dt_cnt.apply(lambda x:int(x) if x!=-1 else 0)
    temp['cur_credit_min_opn_dt_cnt'] = temp.cur_credit_min_opn_dt_cnt.apply(lambda x:int(x) if x!=-1 else 0)
    #理财产品，基金，保险，黄金占比
    temp_name = ['l12mon_buy_fin_mng_whl_tms','l12_mon_fnd_buy_whl_tms','l12_mon_insu_buy_whl_tms', 'l12_mon_gld_buy_whl_tms']
    temp['all_buy_count'] = temp['l12mon_buy_fin_mng_whl_tms'] + temp['l12_mon_fnd_buy_whl_tms'] + temp['l12_mon_insu_buy_whl_tms'] +temp['l12_mon_gld_buy_whl_tms']
    temp['all_buy_count_temp'] = temp['all_buy_count'].apply(lambda x:x if x!=0 else 0.1)
    for name in temp_name:
        new_name = name + '_ratio'
        temp[new_name] = temp[name] / temp['all_buy_count_temp']
    #平均每卡持有天数
    temp['debit_temp'] = temp['cur_debit_cnt'].apply(lambda x:x if x!=0 else 0.1)
    temp['credit_temp'] = temp['cur_credit_cnt'].apply(lambda x:x if x!=0 else 0.1)
    temp['debit/cnt'] = temp['cur_debit_min_opn_dt_cnt']/temp['debit_temp']
    temp['credit/cnt'] = temp['cur_credit_min_opn_dt_cnt']/temp['credit_temp']
    temp = temp.drop(['debit_temp','credit_temp', 'all_buy_count_temp'],axis=1)
    return temp


def get_trd_feature(data_trd, data):

    data = get_time_feature(train_trd, data, time_name='trx_tm', catgory_name='Trx_Cod1_Cd', phase='trd')
    data = get_time_feature(train_trd[train_trd['Dat_Flg1_Cd'] == 'C'], data, time_name='trx_tm', catgory_name='Trx_Cod1_Cd', phase='c')
    data = get_time_feature(train_trd[train_trd['Dat_Flg1_Cd'] == 'B'], data, time_name='trx_tm', catgory_name='Trx_Cod1_Cd', phase='b')

    #最后一笔交易的情况
    temp = train_trd.sort_values('trx_tm',ascending=False).groupby('id').first().reset_index().drop(['flag','trx_tm'],axis=1)
    temp.columns = temp.columns.map(lambda x: x + '__last' if x!='id' else x )
    temp_name = ['Dat_Flg1_Cd__last', 'Dat_Flg3_Cd__last','Trx_Cod1_Cd__last','Trx_Cod2_Cd__last']
    for i in temp_name :
            temp[i] = temp[i].astype('category').cat.codes
    data = pd.merge(data, temp, on=['id'], how='left')
    for i in temp_name:
        data[i].fillna(-1, inplace=True)
    data['cny_trx_amt__last'].fillna(0, inplace=True)
     
    # 只考虑了天数
    data_trd['trx_tm'] = data_trd.trx_tm.apply(lambda x: x.split()[0])
    # 用户交易条目数和交易天数 平均每天交易数，总收入交易数 支出交易数
    temp = train_trd.groupby('id', as_index=False)['Dat_Flg1_Cd'].agg({'trd_count': 'count'})
    data = pd.merge(data, temp, on=['id'], how='left')
    data['trd_count'].fillna(0, inplace=True)

    temp = train_trd.groupby('id', as_index=False)['trx_tm'].agg({'trx_tm_count': 'nunique'})
    data = pd.merge(data, temp, on=['id'], how='left')
    data['trx_tm_count'].fillna(0, inplace=True)
    
    data['temp_trd_count'] = data['trd_count'].apply(lambda x: x if x!=0 else 0.1)
    data['temp_trx_tm_count'] = data['trx_tm_count'].apply(lambda x: x if x!=0 else 0.1)
    
    data['trans_day_mean'] = data['trd_count'] / data['temp_trx_tm_count']

    ## 用户  收入 支出 条目、天平均
    temp_name = []
    c_temp_dict = collections.OrderedDict()
    b_temp_dict = collections.OrderedDict()
    for i in ['count','sum','std','min','max','mean','median']:
        c_temp_dict['c_'+i] = i
        b_temp_dict['b_'+i] = i
    
    temp = train_trd[train_trd['Dat_Flg1_Cd'] == 'C'].groupby('id', as_index=False)['cny_trx_amt'].agg(c_temp_dict)
    data = pd.merge(data, temp, on=['id'], how='left')
    temp = train_trd[train_trd['Dat_Flg1_Cd'] == 'C'].groupby('id', as_index=False)['cny_trx_amt'].agg({'c_skew':sp.stats.skew})
    data = pd.merge(data, temp, on=['id'], how='left')
    temp_name.append('c_skew')
    temp = train_trd[train_trd['Dat_Flg1_Cd'] == 'C'].groupby('id', as_index=False)['cny_trx_amt'].agg({'c_kurt':sp.stats.kurtosis})
    data = pd.merge(data, temp, on=['id'], how='left')
    temp_name.append('c_kurt')

    temp = train_trd[train_trd['Dat_Flg1_Cd'] == 'B'].groupby('id', as_index=False)['cny_trx_amt'].agg(b_temp_dict)
    data = pd.merge(data, temp, on=['id'], how='left')
    temp = train_trd[train_trd['Dat_Flg1_Cd'] == 'B'].groupby('id', as_index=False)['cny_trx_amt'].agg({'b_skew': sp.stats.skew})
    data = pd.merge(data, temp, on=['id'], how='left')
    temp_name.append('b_skew')
    temp = train_trd[train_trd['Dat_Flg1_Cd'] == 'B'].groupby('id', as_index=False)['cny_trx_amt'].agg({'b_kurt':sp.stats.kurtosis})
    data = pd.merge(data, temp, on=['id'], how='left')
    temp_name.append('b_kurt')

    for c,b in zip(c_temp_dict.keys(),b_temp_dict.keys()):
        
        data[c].fillna(0, inplace=True)
        data[b].fillna(0, inplace=True)
        
        name = c + "_add_" + b
        temp_name.append(name)
        data[name] = data[c] + data[b]

        name = c + "_sub_" + b
        temp_name.append(name)
        data[name] = data[c] - data[b]
    
    name = 'c_max' + "_sub__" + 'b_min'                                                                                                                        
    temp_name.append(name)                                                                                                                        
    data[name] = data['c_max'] - data['b_min']
    
    def get_account_category(x):
        if x < 0:
            return 0
        elif x > 0:
            return 1
        else:
            return 2
    data['cur_account'] = data['c_sum_add_b_sum'].apply(get_account_category)

    temp = train_trd[train_trd['Dat_Flg1_Cd'] == 'C'].groupby('id', as_index=False)['trx_tm'].agg({'c_days':'nunique'})                                   
    data = pd.merge(data, temp, on=['id'], how='left')
    temp_name.append('c_days')
    data['c_days'].fillna(0, inplace=True)

    temp = train_trd[train_trd['Dat_Flg1_Cd'] == 'B'].groupby('id', as_index=False)['trx_tm'].agg({'b_days':'nunique'})                                   
    data = pd.merge(data, temp, on=['id'], how='left')
    temp_name.append('b_days')
    data['b_days'].fillna(0, inplace=True)
    #总收益
    all_temp_dict = collections.OrderedDict()
    for i in ['mean','std','median']:
        all_temp_dict['all_' + i] = i
    temp = train_trd.groupby('id', as_index=False)['cny_trx_amt'].agg(all_temp_dict)                                                         
    data = pd.merge(data, temp, on=['id'], how='left')
    temp = train_trd.groupby('id', as_index=False)['cny_trx_amt'].agg({'all_skew':sp.stats.skew})
    data = pd.merge(data, temp, on=['id'], how='left')
    temp_name.append('all_skew')
    temp = train_trd.groupby('id', as_index=False)['cny_trx_amt'].agg({'all_kurt': sp.stats.kurtosis})
    data = pd.merge(data, temp, on=['id'], how='left')
    temp_name.append('all_kurt')
    
    for i in all_temp_dict.keys():
        data[i].fillna(0, inplace=True)
    temp_name = temp_name + c_temp_dict.keys() + b_temp_dict.keys() + all_temp_dict.keys()
    for i in temp_name:
        col = i + '/trd_count'
        data[col] = data[i] / data['temp_trd_count']
        col = i + '/trx_tm_count'
        data[col] = data[i] / data['temp_trx_tm_count']

    ## 用户 三种支付方式不同类型计数占比
    temp = train_trd.groupby(['id', 'Dat_Flg3_Cd'])['Dat_Flg3_Cd'].count().unstack().reset_index()
    data = pd.merge(data, temp, on=['id'], how='left')
    
    train_trd['Trx_Cod1_Cd'] = train_trd['Trx_Cod1_Cd'].apply(lambda x: str(x))
    temp = train_trd.groupby(['id', 'Trx_Cod1_Cd'])['Trx_Cod1_Cd'].count().unstack().reset_index().rename(columns={'1':
        'Trx_Cod1_Cd_1_count', '2': 'Trx_Cod1_Cd_2_count', '3': 'Trx_Cod1_Cd_3_count'})
    data = pd.merge(data, temp, on=['id'], how='left')
    
    
    temp = train_trd.groupby(['id', 'Trx_Cod2_Cd'])['Trx_Cod2_Cd'].count().unstack().reset_index()
    temp.columns = temp.columns.map(lambda x: str(x))
    #temp.columns = temp.columns.map(lambda x: x+"_Cd")
    #temp.rename(columns={'id_Cd':'id'}, inplace = True)
    temp_name = temp.columns.tolist()[1:]
    data = pd.merge(data, temp, on=['id'], how='left')
    
    for i in ['A', 'B', 'C', 'Trx_Cod1_Cd_1_count', 'Trx_Cod1_Cd_2_count', 'Trx_Cod1_Cd_3_count'] + temp_name:
        data[i] = data[i].apply(lambda x: x if x == x else 0)
        col = i + "/trd_count"
        data[col] = data[i] / data['temp_trd_count']
        col = i + "/trd_mx_count"
        data[col] = data[i] / data['temp_trx_tm_count']

    ## 用户 交易的第一天和最后一天
    temp = train_trd.groupby('id', as_index=False)['trx_tm'].agg({'trx_tm_first': 'min', 'trx_tm_last':
        'max'})
    data = pd.merge(data, temp, on=['id'], how='left')
      
    #data['trx_tm_first'] = data['trx_tm_first'].astype('category').cat.codes
    #data['trx_tm_last'] = data['trx_tm_last'].astype('category').cat.codes 
    data['first_day'] = train_trd['trx_tm'].min()
    data['trx_tm_first'] = pd.to_datetime(data['trx_tm_first'])-pd.to_datetime(data['first_day'])                                                                   
    data['trx_tm_first'] = data.trx_tm_first.apply(lambda x:int(x.days) if x==x else 0)
    data['trx_tm_last'] = (pd.to_datetime(data['trx_tm_last'])-pd.to_datetime(data['first_day']))
    data['trx_tm_last'] = data.trx_tm_last.apply(lambda x:int(x.days) if x==x else 0)


    #收支一级分类,每个分类的最大值，最小值，平均值，总和

    for i in ['min','max','mean','sum','count']:
        name = "cny_trx_amt__" + i
        temp = train_trd.groupby(['id', 'Trx_Cod1_Cd'], as_index=False)['cny_trx_amt'].agg({name:i})
        temp = pd.pivot_table(temp[['id', 'Trx_Cod1_Cd', name]], index=['id','Trx_Cod1_Cd']).unstack().reset_index().fillna(0)
        data = pd.merge(data, temp, on=['id'], how='left')
        data.columns = data.columns.map(lambda x: x if name  not in x else x[0] +'_' +str(x[1]) )
    for i in ['sum','mean','count','max','min']:
        name = "b_cny_trx_amt__" + i
        temp = train_trd[train_trd['Dat_Flg1_Cd'] == 'B'].groupby(['id','Trx_Cod1_Cd'],as_index=False)['cny_trx_amt'].agg({name:i})
        temp = pd.pivot_table(temp[['id', 'Trx_Cod1_Cd', name]], index=['id','Trx_Cod1_Cd']).unstack().reset_index().fillna(0)
        data = pd.merge(data, temp, on=['id'], how='left')
        data.columns = data.columns.map(lambda x: x if name  not in x else x[0] +'_' +str(x[1]) )
        name = "c_cny_trx_amt__" + i
        temp = train_trd[train_trd['Dat_Flg1_Cd'] == 'C'].groupby(['id','Trx_Cod1_Cd'],as_index=False)['cny_trx_amt'].agg({name:i})
        temp = pd.pivot_table(temp[['id', 'Trx_Cod1_Cd', name]], index=['id','Trx_Cod1_Cd']).unstack().reset_index().fillna(0)
        data = pd.merge(data, temp, on=['id'], how='left')
        data.columns = data.columns.map(lambda x: x if name  not in x else x[0] +'_' +str(x[1]) )



    data = data.drop(['first_day','temp_trd_count','temp_trx_tm_count'], axis = 1)
    return data


def get_beh_feature(train_beh, data):
    data = get_time_feature(train_beh, data, time_name='page_tm', catgory_name='page_no', phase='beh')
    #天数
    train_beh['day'] = train_beh['page_tm'].apply(get_day)
    train_beh['hour'] = train_beh['page_tm'].apply(lambda x: int(x[11:13]))
    train_beh['week'] = train_beh['day'].apply(get_week)

    temp = train_beh.sort_values('page_tm',ascending=False).groupby('id').first().reset_index().drop(['flag','page_tm'],axis=1)
    temp.columns = temp.columns.map(lambda x: x + '__last' if x!='id' else x )
    temp_name = ['page_no__last']
    for i in temp_name :
        temp[i] = temp[i].astype('category').cat.codes
    data = pd.merge(data, temp, on=['id'], how='left')                                                                                                
    for i in temp_name:
        data[i].fillna(-1, inplace=True)
    
    # 只考虑了天数
    train_beh['page_tm'] = train_beh['page_tm'].apply(lambda x: x.split()[0])
    # 用户总访问次数，平均每天访问次数
    temp = train_beh.groupby('id', as_index=False)['page_tm'].agg({'beh_count': 'count'})
    data = pd.merge(data, temp, on=['id'], how='left')
    data['beh_count'].fillna(0, inplace=True)

    temp = train_beh.groupby('id', as_index=False)['page_tm'].agg({'beh_day_count': 'nunique'})
    data = pd.merge(data, temp, on=['id'], how='left')
    data['beh_day_count'].fillna(0, inplace=True)

    data['temp_beh_count'] = data.beh_count.apply(lambda x:x if x!=0 else 0.1)
    data['temp_beh_day_count'] = data.beh_day_count.apply(lambda x:x if x!=0 else 0.1)
    
    data['beh_day_mean'] = data['beh_count'] / data['beh_day_count']

    # 用户访问的总页面编码种类
    temp = train_beh.groupby('id', as_index=False)['page_no'].agg({'page_no_count': 'nunique'})
    data = pd.merge(data, temp, on=['id'], how='left')
    data['page_no_count'].fillna(0, inplace=True)

    # 访问各个页面编码的占比
    
    temp = train_beh.groupby(['id', 'page_no'])['page_no'].count().unstack().reset_index()
    data = pd.merge(data, temp, on=['id'], how='left')
    temp_name = list(set(train_beh['page_no'].tolist()))
    for i in temp_name:
        data[i] = data[i].apply(lambda x: x if x == x else 0)
        col = i + "_ratio"
        data[col] = data[i] / data['temp_beh_count']
    
    temp = train_beh.groupby('id', as_index=False)['page_tm'].agg({'page_tm_first': 'min', 'page_tm_last':'max'})                                                                                                                                       
    data = pd.merge(data, temp, on=['id'], how='left')
    data['first_day'] = train_beh['page_tm'].min()
    data['page_tm_first'] = pd.to_datetime(data['page_tm_first'])-pd.to_datetime(data['first_day'])                                                                   
    data['page_tm_last'] = pd.to_datetime(data['page_tm_last'])-pd.to_datetime(data['first_day'])                                                                   
    data['page_tm_first'] = data.page_tm_first.apply(lambda x:int(x.days) if x==x else 0)
    data['page_tm_last'] = data.page_tm_last.apply(lambda x:int(x.days) if x==x else 0)
    data = data.drop(['first_day','temp_beh_count','temp_beh_day_count'], axis = 1)
    return data


def get_feature(data_tag,data_trd,data_beh,flag_train):
    if flag_train:
        data_beh['page_tm'] = data_beh['Unnamed: 3']
        data_beh = data_beh.drop(['Unnamed: 3'], axis = 1)
    else:
        data_beh['page_tm'] = data_beh['Unnamed: 2']
        data_beh = data_beh.drop(['Unnamed: 2'], axis = 1)
    data_tag = get_tag_feature(data_tag)
    data_tag = get_trd_feature(data_trd,data_tag)
    data_tag = get_beh_feature(data_beh,data_tag)

    return data_tag



data = get_feature(data_tag,data_trd,data_beh,True)
#data.fillna(0, inplace=True)
train_data = data[data['train_flag']==0]
test_data = data[data['train_flag']==1]
y = train_data['flag'].values
train_data = train_data.drop(['flag','id','train_flag'], axis = 1)
test_id = test_data['id'].values
test_data = test_data[column_name]
train_data = train_data[column_name]

print(train_data.shape)
print(test_data.shape)
#训练模型
n_fold = 3
#folds = KFold(n_splits=n_fold, shuffle=True)
folds = StratifiedKFold(n_splits=n_fold, shuffle=True)

def train_model(X=train_data.values, y=y, featurename=column_name, X_test=test_data.values, params=None, folds=folds,
                model_type='lgb', plot_feature_importance=False, model=None):
    oof = np.zeros(len(X))
    prediction = np.zeros(len(X_test))
    scores = []
    feature_importance = pd.DataFrame()
    for fold_n, (train_index, valid_index) in enumerate(folds.split(X,y)):
        print('Fold', fold_n, 'started at', time.ctime())
        X_train, X_valid = X[train_index], X[valid_index]
        y_train, y_valid = y[train_index], y[valid_index]
        if model_type == 'lgb':
            train_data = lgb.Dataset(data=X_train, label=y_train)
            valid_data = lgb.Dataset(data=X_valid, label=y_valid)
            model = lgb.train(params, train_data, num_boost_round=20000,
                              valid_sets=[train_data, valid_data], verbose_eval=1000, early_stopping_rounds=200)

            y_pred_valid = model.predict(X_valid)
            y_pred = model.predict(X_test, num_iteration=model.best_iteration)

        if model_type == 'xgb':
            train_data = xgb.DMatrix(data=X_train, label=y_train, feature_names=featurename)
            valid_data = xgb.DMatrix(data=X_valid, label=y_valid, feature_names=featurename)
            watchlist = [(train_data, 'train'), (valid_data, 'valid_data')]
            model = xgb.train(dtrain=train_data, num_boost_round=15000, evals=watchlist, early_stopping_rounds=200,
                              verbose_eval=50, params=params)
            y_pred_valid = model.predict(xgb.DMatrix(X_valid, feature_names=featurename),
                                         ntree_limit=model.best_ntree_limit)
            y_pred = model.predict(xgb.DMatrix(X_test, feature_names=featurename), ntree_limit=model.best_ntree_limit)
        
        
        if model_type == 'sklearn':
            model = model
            model.fit(X_train, y_train)
            y_pred_valid = model.predict(X_valid).reshape(-1)
            y_pred = model.predict(X_test).reshape(-1,)
        
        
        '''
        if model_type == 'rcv':
            model = RidgeCV(alphas=(0.01, 0.1, 1.0, 10.0, 100.0), scoring='neg_mean_absolute_error', cv=3)
            model.fit(X_train, y_train)
            print(model.alpha_)

            y_pred_valid = model.predict(X_valid).reshape(-1, )
            score = mean_absolute_error(y_valid, y_pred_valid)
            print(f'Fold {fold_n}. MAE: {score:.4f}.')
            print('')
            y_pred = model.predict(X_test).reshape(-1, )


        if model_type == 'cat':
            model = CatBoostRegressor(iterations=20000, eval_metric='auc', **params)
            model.fit(X_train, y_train, eval_set=(X_valid, y_valid), cat_features=[], use_best_model=True,
                      verbose=False)
            y_pred_valid = model.predict(X_valid)
            y_pred = model.predict(X_test)
        '''


        #y_pred_valid = MinMaxScaler(copy=True,feature_range=(0,1)).fit_transform(y_pred_valid.reshape(-1,1))
        #y_pred = MinMaxScaler(copy=True,feature_range=(0,1)).fit_transform(y_pred.reshape(-1,1)).reshape(-1,)

        oof[valid_index] = y_pred_valid.reshape(-1, )
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
            fold_importance = model.get_fscore()
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

            plt.figure(figsize=(16, 26))
            sns.barplot(x="importance", y="feature", data=best_features.sort_values(by="importance", ascending=False))
            plt.title('LGB Features (avg over folds)')

            return oof, prediction, feature_importance
        return oof, prediction, feature_importance

    elif model_type == 'xgb':
        feature_importance['importance'] /= n_fold
        if plot_feature_importance:
            plt.figure(figsize=(16, 26))
            feature_importance.plot(kind='barh', x='feature', y='importance', legend=False, figsize=(6, 10))
            plt.title('XGB Features (avg over folds)')
            plt.xlabel('relative importance')
            plt.show()
            return oof, prediction, feature_importance
        return oof, prediction, feature_importance
    else:
        return oof, prediction


xgb_params = {'eta':0.03,
          'max_depth':5,
          'subsample':0.5,
          'colsample_bytree':0.5,
          'alpha':0.1,
          'min_samples_split':10,
          'min_samples_leaf':10,
          'max_leaf_nodes':10,
          'scale_pos_weight':3,
          'nthread':7,
          'objective':'binary:logistic',
          'eval_metric' : "auc",
          'booster' : "gbtree"}

oof_xgb, prediction_xgb ,feature = train_model(params=xgb_params, model_type='xgb',plot_feature_importance=False)
print(feature)
feature.to_csv('feature.csv')

savepath = "./result.txt"
with open(savepath, "w") as f:
    for user_id,score in zip(test_id,prediction_xgb):
        f.write(user_id + '\t' +str(score) +'\n')
savepath = "./test.txt"
with open(savepath, "w") as f:
    for user_id,score in zip(y,oof_xgb):
        f.write(str(user_id) + '\t' +str(score) +'\n')
