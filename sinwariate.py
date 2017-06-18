# -*- coding: utf-8 -*-

triple = pd.read_csv("C:/tmp/Evaluation/Triple.txt",header=None)
triple["tri"] = triple[0]+triple[1]+triple[2]
results = pd.read_csv("C:/tmp/Evaluation/Results2.txt", header=None)
data = pd.read_csv("C:/tmp/Evaluation/data_learning.csv")
#data = pd.read_csv("C:/tmp/Evaluation/data_predict.csv")


data["tri"] = data[u"体言".encode("shift-jis")]+data[u"助詞".encode("shift-jis")]+data[u"用言".encode("shift-jis")]
i=0
sinsou = []
for j,line in enumerate(data[u"tri".encode("shift-jis")]):

    if i==len(triple)-1:
        sinsou.append(data[u"深層格".encode('shift-jis')][j])
        print "last", line.decode("shift-jis"),triple.ix[i-1,"tri"].decode("shift-jis"),"j=%d" %j,"i=%d" %i        
        break
        
    while line == triple.ix[i,"tri"]:
        sinsou.append(data[u"深層格".encode('shift-jis')][j])
        i+=1
        print line.decode("shift-jis"),triple.ix[i-1,"tri"].decode("shift-jis"),"j=%d" %j,"i=%d" %i
'''
triple.rename(columns={0:u'名詞'.encode('shift-jis'),1:u'助詞'.encode('shift-jis'),2:u'動詞'.encode('shift-jis')},inplace=True)
results.rename(columns={0:u'名詞クラス'.encode('shift-jis'),1:u'助詞クラス'.encode('shift-jis'),2:u'動詞クラス'.encode('shift-jis'),3:u'置き換え助詞'.encode('shift-jis'),4:u'予測結果'.encode('shift-jis')},inplace=True)
tmpframe = pd.concat([triple,results],axis=1)
tmpframe[u'深層格'.encode('shift-jis')]=sinsou
EvaFrame = DataFrame(tmpframe, columns=[u"名詞".encode('shift-jis'),u"助詞".encode('shift-jis'),u"動詞".encode('shift-jis'),u"名詞クラス".encode('shift-jis'),u"助詞クラス".encode('shift-jis'),u"動詞クラス".encode('shift-jis'),u"置き換え助詞".encode('shift-jis'),u"予測結果".encode('shift-jis'),u"深層格".encode('shift-jis')])
EvaFrame.to_csv("C:/tmp/Evaluation/Evadata.csv")




'''        
    




'''
NPList=[]
for i, str in enumerate(data[u"体言".encode("shift-jis")]):
    lan = Language(str)
    print i

    Noun =""
    for word in lan.getMorpheme():
        Mor = word.split(",")
        Noun +=Mor[0]
    
    if Mor[3].decode("shift-jis").encode("utf-8")=="人名":
        NPList.append(u"固有人名".encode("shift-jis"))
    elif Mor[3].decode("shift-jis").encode("utf-8")=="地域":
        NPList.append(u"固有地名".encode("shift-jis"))
    else:
        NPList.append(Noun)

'''