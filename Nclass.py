# -*- coding: utf-8 -*-
from pandas import DataFrame
import pandas as pd
import numpy 
from numpy import NaN

'''
data_exp= pd.read_csv("C:/tmp/Evaluation/data_exp.csv",encoding='shift-jis',index_col=0)
f = pd.read_csv(u"D:/研究/データ/bunruidb/bunruidb.txt",header=None,encoding='shift-jis')
'''
class bunrui:

    def __init__(self, f):    
        bunruidb = DataFrame(f,columns={3,5,12})
        Nbunrui = bunruidb[bunruidb[3]==u"体"]
        Nbunrui.drop_duplicates(inplace = True)
        keys=[]
        values=[]
        for i in Nbunrui[12].drop_duplicates():
            print i
            keys.append(i)
            values.append(list(Nbunrui.ix[Nbunrui[12]==i,5]))
        self.Nclass = dict(zip(keys,values))

        
    def to_class(self, data_exp):
        data_expclass = data_exp
        fnc = lambda x: self.Nclass.get(x,NaN)
        data_expclass[u"名詞クラス"] = data_expclass[u"体言"].map(fnc)
        
        compN_frame = DataFrame(columns = [u'体言', u'名詞クラス', u'助詞', u'用言', u'動詞クラス', u'深層格', u'表層格'])
        compNline = []
        for i, line in enumerate(data_expclass[u"名詞クラス"]):
            print i
            if type(line) is not unicode and type(line) is not float:
                compNline.append(False)
                for NC in line:
                    tmp_frame = DataFrame(data_expclass.ix[i,:]).T
                    tmp_frame[u"名詞クラス"]=NC           
                    compN_frame = pd.concat([compN_frame,tmp_frame],axis=0)
                    #print compN_frame
                    #print NC
            else:
                compNline.append(True)
        
        data_expclass[compNline]
        data_expclass = pd.concat([data_expclass[compNline],compN_frame],axis=0)
        data_expclass.reset_index(inplace=True)
        del data_expclass['index']
        #data_expclass.rename(columns={u"体言":u"名詞クラス"},inplace=True)
        data_expclass.drop_duplicates(inplace = True)
        return data_expclass, compN_frame

'''
from Nclass import bunrui
bun = bunrui(f)
data_expclass, compN_frame= bun.to_class(data_exp)
data_expclass.to_csv("C:/tmp/Evaluation/data_expclass.csv",encoding="shift-jis")
compN_frame.reset_index(inplace=True)
del compN_frame['index']
sampler = np.random.permutation(len(compN_frame))
data_learning = compN_frame.take(sampler[:len(sampler)/2])
data_predict = compN_frame.take(sampler[len(sampler)/2:])
data_learning.to_csv("C:/tmp/Evaluation/dataclass_learning.csv",encoding='shift-jis')
data_predict.to_csv("C:/tmp/Evaluation/dataclass_predict.csv",encoding='shift-jis')
'''
'''
grouped = data_expclass.groupby(u"深層格")
from collections import Counter
DataFrame(grouped[u"動詞クラス"].apply(lambda x: Counter(x))).reset_index().sort([u"深層格",0],ascending=False)
'''
