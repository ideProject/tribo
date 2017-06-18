# -*- coding: utf-8 -*-
from pandas import DataFrame
import pandas as pd
def exdata(f):
    data=DataFrame()
    for i in range(1,6):
        tmpframe=DataFrame(f,columns= ['見出し語','格%d(事例)' %i,'格%d(深層格)' %i,'格%d(表層格)' %i, '大分類2'])
        tmpframe=tmpframe.rename(columns= {'見出し語':'用言','格%d(事例)' %i:'体言助詞','格%d(深層格)' %i:'深層格','格%d(表層格)' %i:'表層格', '大分類2':'動詞クラス'})
        data = pd.concat([data,tmpframe],ignore_index=True)
    data = data.ix[data[u"体言助詞".encode("utf-8")].notnull(),:]
    data = data.ix[data[u"表層格".encode("utf-8")].notnull(),:]
    data = data.reset_index()
    del data[u'index']
    return data


'''
NPlist=[]
for i,str in enumerate(data[u"体言助詞".encode('utf-8')]):
#for i,str in enumerate(data.ix[:,2]):
    print i
    lan=Language(str)
    NPlist.extend(lan.getMorpheme())
'''
'''
NList=[]
PList=[]
OtherList=[]
tmpword = NPlist[0].split(",")[0]
wflag = True
for i,line in enumerate(NPlist):
    new_line = line.split(",")
    if i == len(NPlist)-1:
        break
    
    next_line = NPlist[i+1].split(",")
                
    if wflag == True:
        tmpword = new_line[0]
             
    if new_line[1]!=next_line[1]:
        if new_line[1].decode('shift-jis')==u"名詞" and next_line[1].decode('shift-jis')==u"助詞":
            NList.append(tmpword)
            PList.append(next_line[0])
        else:
            OtherList.append(tmpword)
        wflag = True
    else:
        tmpword += next_line[0]
        wflag = False
'''
'''
NP=[]
for i,str in enumerate(NList):
    NP.append(str+PList[i])

for i, str in enumerate(NP):
    print i
    indexList = data[u"体言助詞".encode("utf-8")][data[u"体言助詞".encode("utf-8")]==str.decode('shift-jis').encode('utf-8')].index.tolist()
    for ii in indexList:
        data.ix[ii, "体言"] = NList[i].decode('shift-jis')
        data.ix[ii, "助詞"] = PList[i].decode('shift-jis')

'''
'''
data = data[data['深層格']!="起点・着点"]
data = data[data['深層格']!="その他"]
data = data[data['体言'].notnull()]
data.reset_index(inplace=True)
del data['index']
data_exp = DataFrame(data,columns=["体言","助詞","用言","深層格","表層格","動詞クラス"])

fs = lambda x: sindict.get(x,x)
data_exp["深層格"] = data_exp["深層格"].map(fs)
fh = lambda x: hyoudict.get(x,x)
data_exp["表層格"] = data_exp["表層格"].map(fh)
fc = lambda x: sinbunrui.get(x,x)
data_exp["深層格"] = data_exp["深層格"].map(fc)


data_exp.to_csv("C:/tmp/Evaluation/data_exp.csv",encoding='shift-jis')
sampler = np.random.permutation(len(data_exp))
data_learning = data_exp.take(sampler[:len(sampler)/2])
data_predict = data_exp.take(sampler[len(sampler)/2:])
data_learning.to_csv("C:/tmp/Evaluation/data_learning.csv",encoding='shift-jis')
data_predict.to_csv("C:/tmp/Evaluation/data_predict.csv",encoding='shift-jis')



'''