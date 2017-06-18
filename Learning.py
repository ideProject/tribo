# -*- coding: utf-8 -*-
'''
grouped = EvaFrame.groupby(u'予測結果'.encode('shift-jis'))
from collections import Counter
bunrui = DataFrame(grouped[u'深層格'.encode('shift-jis')].apply(lambda x:Counter(x)))

bunrui2 = bunrui.unstack()
bunrui2_1 = bunrui2.drop('null')
bunrui2_1.columns = bunrui2_1.columns.get_level_values(1)
sum_line =  bunrui2_1.sum(0)
sum_row = bunrui2_1.sum(1)
for i,sum0 in enumerate(sum_row):
    for j,sum1 in enumerate(sum_line):
        bunrui2_1.ix[i,j] = bunrui2_1.ix[i,j]*2/(sum1+sum0)

        
bunrui2_1.rename(columns={bunrui2_1.columns[0]:bunrui2_1.columns[0].decode('shift-jis'),bunrui2_1.columns[1]:bunrui2_1.columns[1].decode('shift-jis'),bunrui2_1.columns[2]:bunrui2_1.columns[2].decode('shift-jis'),bunrui2_1.columns[3]:bunrui2_1.columns[3].decode('shift-jis'),bunrui2_1.columns[4]:bunrui2_1.columns[4].decode('shift-jis'),bunrui2_1.columns[5]:bunrui2_1.columns[5].decode('shift-jis'),bunrui2_1.columns[6]:bunrui2_1.columns[6].decode('shift-jis')})

'''                        
sinclus = {
            u"関係".encode('shift-jis'):[3],
            u"主体".encode('shift-jis'):[1,2],
            u"状況".encode('shift-jis'):[3],
            u"対象".encode('shift-jis'):[1,2],
            u"着点".encode('shift-jis'):[1,6],
            u"道具".encode('shift-jis'):[3],
            u"変化前".encode('shift-jis'):[4,5]
}

'''
fsin = lambda x: sinclus.get(x,x)
#EvaFrame[u'深層格'.encode('shift-jis')] = EvaFrame[u'深層格'.encode('shift-jis')].map(fsin)
EvaFrame[u'深層格クラスタ'.encode('shift-jis')] = EvaFrame[u'深層格'.encode('shift-jis')].map(fsin)
'''