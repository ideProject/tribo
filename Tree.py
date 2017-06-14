# -*- coding: utf-8 -*-
data_expclass = pd.read_csv("C:/tmp/Evaluation/data_expclass.csv",encoding="shift-jis")

data_expclass2 = data_expclass

data_expclass2 = data_expclass2[data_expclass2[u"名詞クラス"].notnull()] 
data_expclass2.reset_index(inplace=True)
del data_expclass2[u"index"]
'''
data_expclass2[u"名詞クラス"] = data_expclass2[u"名詞クラス"].str.encode("utf-8")
data_expclass2[u"助詞"] = data_expclass2[u"助詞"].str.encode("utf-8")
data_expclass2[u"動詞クラス"] = data_expclass2[u"動詞クラス"].str.encode("utf-8")
data_expclass2[u"深層格"] = data_expclass2[u"深層格"].str.encode("utf-8")
'''

Ndict = dict(zip(list(data_expclass2[u'名詞クラス'].drop_duplicates()), range(len(data_expclass2[u'名詞クラス'].drop_duplicates()))))
Vdict = dict(zip(list(data_expclass2[u'動詞クラス'].drop_duplicates()), range(len(data_expclass2[u'動詞クラス'].drop_duplicates()))))
Pdict = dict(zip(list(data_expclass2[u'助詞'].drop_duplicates()), range(len(data_expclass2[u'助詞'].drop_duplicates()))))
Ddict = dict(zip(list(data_expclass2[u'深層格'].drop_duplicates()), range(len(data_expclass2[u'深層格'].drop_duplicates()))))
fnd = lambda x: Ndict.get(x,NaN)
data_expclass2[u"名詞クラス"] = data_expclass2[u"名詞クラス"].map(fnd)
fvd = lambda x: Vdict.get(x,NaN)
data_expclass2[u"動詞クラス"] = data_expclass2[u"動詞クラス"].map(fvd)
fpd = lambda x: Pdict.get(x,NaN)
data_expclass2[u"助詞"] = data_expclass2[u"助詞"].map(fpd)
fdd = lambda x: Ddict.get(x,NaN)
data_expclass2[u"深層格"] = data_expclass2[u"深層格"].map(fdd)

data_expclass2 = data_expclass2[data_expclass2[u"名詞クラス"].notnull()] 
data_expclass2.reset_index(inplace=True)
del data_expclass2[u"index"]


from sklearn import tree
#X=[data_expclass2[u"名詞クラス"],data_expclass2[u"動詞クラス"],data_expclass2[u"助詞"]]
X=[]
for i,line in enumerate(data_expclass2[u"名詞クラス"]):
    X.append([line,data_expclass2[u"動詞クラス"][i],data_expclass2[u"助詞"][i]])

Y=data_expclass2[u"深層格"]
clf = tree.DecisionTreeClassifier()
clf.fit(X,Y)

predicted = clf.predict(X)
float(len(Y[predicted == Y])) / float(len(Y))
premat = pd.concat([DataFrame(predicted,columns=[u"予測結果"]),DataFrame(Y)],axis=1)
grouped = premat.groupby(u'予測結果')
precount = grouped[u'深層格'].apply(lambda x: Counter(x))
premat = precount.unstack().fillna(0)
Ddict_inv = {v:k for k, v in Ddict.items()}
fddi = lambda x: Ddict_inv.get(x,NaN)
premat.index = premat.index.map(fddi)
premat.columns = premat.columns.map(fddi)
premat[u"合計"] = premat.sum(1)
for i in premat.index:
    premat.ix[i,u"予測率"] = premat.ix[i,i]/premat.ix[i,u"合計"]


from sklearn.externals.six import StringIO
dot_data = StringIO()
tree.export_graphviz(clf, out_file=dot_data)
import pydotplus
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
from IPython.display import Image
Image(graph.create_png())

