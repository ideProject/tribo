# -*- coding: utf-8 -*-
preList=[]

for i, cluster in enumerate(EvaFrame[u'予測結果'.encode('shift-jis')]):
    corres = False
    for sinN in EvaFrame[u'深層格クラスタ'.encode('shift-jis')][i]:
        if cluster == "null":
            break
        if int(cluster)==sinN:
            corres = True
    if cluster == "null":
        preList.append(NaN)
    elif corres ==True :
        preList.append(True)
    elif corres == False:
        preList.append(False)         
        

EvaFrame[u'正答'.encode('shift-jis')] = preList
grouped = EvaFrame.groupby(u'深層格'.encode('shift-jis'))
sincount = grouped[u'正答'.encode('shift-jis')].apply(lambda x: Counter(x))
prerate = sincount.ix[:,True]/grouped[u'正答'.encode('shift-jis')].count()
prerate.rename(index={prerate.index[0]:prerate.index[0].decode('shift-jis').encode('utf-8'),prerate.index[1]:prerate.index[1].decode('shift-jis'),prerate.index[2]:prerate.index[2].decode('shift-jis'),prerate.index[3]:prerate.index[3].decode('shift-jis'),prerate.index[4]:prerate.index[4].decode('shift-jis'),prerate.index[5]:prerate.index[5].decode('shift-jis'),prerate.index[6]:prerate.index[6].decode('shift-jis')})



