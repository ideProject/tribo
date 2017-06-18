# -*- coding: utf-8 -*-

from pandas import DataFrame
from numpy import NaN
import pandas as pd
import itertools
from Language import Language

class Word_class:
    def __init__(self, NV_class):
        self.Nclass = NV_class[0]
        self.Vclass = NV_class[1]
        
    def makedict(self, Nd, Vd):
        bunruidb = DataFrame(Nd,columns={3,5,12})
        Nbunrui = bunruidb[bunruidb[3]==u"体"]
        Nbunrui.drop_duplicates(inplace = True)
        Nkeys=[]
        Nvalues=[]
        for i in Nbunrui[12].drop_duplicates():
            print i
            Nkeys.append(i)
            Nvalues.append(list(Nbunrui.ix[Nbunrui[12]==i,5]))
        self.Nclass = dict(zip(Nkeys, Nvalues))
        
        #Vbunrui = DataFrame(Vd, columns={u'見出し語', u'大分類1',u'大分類2',u'中分類',u'小分類1',u'小分類2'})        
        Vbunrui = DataFrame(Vd, columns={u'見出し語', u'大分類1',u'大分類2'})        
        Vbunrui.drop_duplicates(inplace = True)
        Vkeys=[]
        Vvalues=[]
        for i in Vbunrui[u'見出し語'].drop_duplicates():
            print i
            Vkeys.append(i)
            Vvalues.append(list(Vbunrui.ix[Vbunrui[u'見出し語']==i,u'大分類2']))
        self.Vclass = dict(zip(Vkeys, Vvalues))
    
    def to_class(self, Noun, Verb):
        if Noun in self.Nclass.keys():
            Nclasslist = self.Nclass[Noun]
        else:
            lan = Language(Noun)
            word = lan.getMorpheme()
            Noun_tail = word[len(word)-1][0]
            if Noun_tail in self.Nclass.keys():
                Nclasslist = self.Nclass[Noun_tail]
            else:
                Nclasslist = [u"未登録"]
        if Verb in self.Vclass.keys():
            Vclasslist = self.Vclass[Verb]
        else:
            Vclasslist =[u"未登録"]
            #print Verb
        NV = []
        for NVclass in itertools.product(Nclasslist,Vclasslist):
            NV.append(NVclass)
        return NV
                
    def to_classF(self, data_exp):
        data_expclass = data_exp
        fnc = lambda x: self.Nclass.get(x,[NaN])
        data_expclass[u"名詞クラス"] = data_expclass[u"名詞"].map(fnc)
        fvc = lambda x: self.Vclass.get(x,[NaN])
        data_expclass[u"動詞クラス"] = data_expclass[u"動詞"].map(fvc)
        
        compN_frame = DataFrame(columns = [u'名詞', u'名詞クラス', u'助詞', u'動詞', u'動詞クラス'])
        
        for i, Nlist, Vlist in enumerate(zip(data_expclass[u"名詞クラス"], data_expclass[u"動詞クラス"])):
            for NVrecord in itertools.product(Nlist * len(Vlist),Vlist * len(Nlist)):
                    tmp_frame = DataFrame(data_expclass.ix[i,:]).T
                    tmp_frame[u"名詞クラス"]=NVrecord[0]
                    tmp_frame[u"動詞クラス"]=NVrecord[1]
                    compN_frame = pd.concat([compN_frame,tmp_frame],axis=0)
        
        return compN_frame
'''
Vf= pd.read_csv("D:/vthesaurus_ver3.csv",encoding='shift-jis',index_col=0)
Nf = pd.read_csv(u"D:/研究/データ/bunruidb/bunruidb.txt",header=None,encoding='shift-jis')

bun_dict = [(vclass_from, vclass_to) for vclass_from, vclass_to in zip(bun_verbs[12],bun_verbs[5])]
bun_Frame = DataFrame(bun_dict)

Vkeys=[]
Vvalues=[]
for i in Vbunrui[u'見出し語'].drop_duplicates():
    if i in list(bun_Frame[0]):   
        Vkeys.append(i)
        Vvalues.append(list(bun_Frame.ix[bun_Frame[0]==i, 1]))
Vclass_bun = dict(zip(Vkeys, Vvalues))        
Verblist = []
Verbclasslist_Vt = []
Verbclasslist_bun = [] 
for i in Vclass_bun.keys():
    for j in Vclass_bun[i]:
        for k in Dc.NV_class[1][i]:
            Verblist.append(i)
            Verbclasslist_Vt.append(j)
            Verbclasslist_bun.append(k)
VerbFrame = DataFrame({u"Verb": Verblist, u"Vthesaurus":Verbclasslist_Vt, u"bunruidb":Verbclasslist_bun})



'''
        