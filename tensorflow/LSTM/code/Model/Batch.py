
# coding: utf-8

# In[ ]:


#https://stackoverflow.com/questions/40994583/how-to-implement-tensorflows-next-batch-for-own-data
import numpy as np
import pandas as pd
from sklearn.utils import shuffle

#np.set_printoptions(threshold=200) 

class Dataset:
    def __init__(self,data):    
        self._index_in_epoch = 0
        self._epochs_completed = 0
        self._data = data
        self._num_examples = data.shape[0]
        pass
    @property
    def data(self):
        return self._data

    def next_batch(self,batch_size):
        start = self._index_in_epoch
        if start == 0 and self._epochs_completed == 0:
            self._data = shuffle(self.data)  
        # go to the next batch
        if start + batch_size > self._num_examples:
            self._epochs_completed += 1
            rest_num_examples = self._num_examples - start
            data_rest_part = self.data.iloc[start:self._num_examples,:]
            self._data = shuffle(self.data)

            start = 0
            self._index_in_epoch = batch_size - rest_num_examples #avoid the case where the #sample != integar times of batch_size
            end =  self._index_in_epoch  
            data_new_part =  self._data.iloc[start:end,:]  
            return pd.concat([data_rest_part,data_new_part],axis=0)
        else:
            self._index_in_epoch += batch_size
            end = self._index_in_epoch
            return self._data.iloc[start:end,:]

