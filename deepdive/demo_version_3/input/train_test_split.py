import sys
import pandas as pd
from os import path
from sklearn.model_selection import train_test_split

root_dir = path.dirname(__file__)
try:
    test_size = float(sys.argv[-1])
    for file_name in sys.argv[1:-1]:
        train_file_dir = file_name+"_train.csv"
        train_file_dir = path.join(root_dir,train_file_dir)
        test_file_dir = file_name+"_test.csv"
        test_file_dir = path.join(root_dir,test_file_dir)
        file_name = file_name+".csv"
        file_dir = path.join(root_dir,file_name)
        df = pd.read_csv(file_dir,header=None)
        m,_ = df.shape
        train_index,test_index = train_test_split(range(m),test_size = test_size,random_state = 65)
        df_train = df.iloc[train_index,:]
        df_test = df.iloc[test_index,:]
        df_train.to_csv(train_file_dir,header=None,index=False)
        df_test.to_csv(test_file_dir,header=None,index=False)
except:
    test_size = 0.4
    for file_name in sys.argv[1:]:
        train_file_dir = file_name+"_train.csv"
        train_file_dir = path.join(root_dir,train_file_dir)
        test_file_dir = file_name+"_test.csv"
        test_file_dir = path.join(root_dir,test_file_dir)
        file_name = file_name+".csv"
        file_dir = path.join(root_dir,file_name)
        df = pd.read_csv(file_dir,header=None)
        m,_ = df.shape
        train_index,test_index = train_test_split(range(m),test_size = test_size,random_state = 65)
        df_train = df.iloc[train_index,:]
        df_test = df.iloc[test_index,:]
        df_train.to_csv(train_file_dir,header=None,index=False)
        df_test.to_csv(test_file_dir,header=None,index=False)

