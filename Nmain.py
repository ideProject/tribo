# -*- coding: utf-8 -*-
import pickle
import pandas as pd
from neural_network import Neural

path_NN = {
    #訓練データ
    "train_data": "data/dataclass_learning.csv",
    #訓練積みニューラルネットワークの保存場所
    "pickle_net": "data/Trained.Network",
    #ニューラルネットワークの入力と出力
    "pickle_dummylist": "data/dummylist.Word",
    #テストデータ
    "test_data": "data/dataclass_predict.csv",
    #ニューラルネットワークの予測結果
    "result_data": "data/data_result.csv"
}
#ニューラルネットワークの学習
'''
data_expclass = pd.read_csv(path_NN["train_data"],encoding="shift-jis")
neu = Neural(data_expclass)
neu.oversample()
Nvector, NS = neu.word_vector(u'名詞クラス',u'深層格')
Vvector, VS = neu.word_vector(u'動詞クラス',u'深層格')
Pvector, PS = neu.word_vector(u'助詞',u'深層格')
Xvector = [Nvector, Vvector, Pvector]
XS = [NS, VS, PS]
dummylist, Ddummy = neu.dummy()
net, ds = neu.neural_data(dummylist[0],dummylist[1],dummylist[2],Ddummy)
net = neu.neural_learn(net, ds)
file = open(path_NN["pickle_net"],'w')
pickle.dump(net, file)
file.close()
file = open(path_NN["pickle_dummylist"],'w')
pickle.dump(dummylist, file)
file.close()
#file = open('D:/tmp/Evaluation/Xvector.Word','w')
#pickle.dump(Xvector, file)
#file.close()
#file = open('D:/tmp/Evaluation/XS.Word','w')
#pickle.dump(XS, file)
#file.close()

precision_perD, recall_perD, resultlist, correctlist = neu.netresult(net, ds)
print precision_perD
'''
#ニューラルネットワークの評価
data_expclass = pd.read_csv(path_NN["test_data"],encoding="shift-jis")
neu2 = Neural(data_expclass)
neu2.data_oversam = neu2.data_expclass
dummylist2, Ddummy2 = neu2.dummy()
Ddummy2.columns = [u"主体", u"起点", u"対象", u"状況", u"着点", u"手段", u"関係"]

file = open(path_NN["pickle_net"])
net = pickle.load(file)
file.close()
file = open(path_NN["pickle_dummylist"])
dummylist = pickle.load(file)
file.close()
#file = open('D:/tmp/Evaluation/Xvector.Word')
#Xvector = pickle.load(file)
#file.close()
#file = open('D:/tmp/Evaluation/XS.Word')
#XS = pickle.load(file)
#file.close()

net2, ds2 = neu2.neural_data(dummylist[0],dummylist[1],dummylist[2],Ddummy2)

precision_perD2, recall_perD2, resultlist, correctlist = neu2.netresult(net, ds2)
print precision_perD2

data_result = neu2.data_oversam
data_result[u'result'] = resultlist
data_result[u'correct'] = correctlist
precision2_perD = neu2.neteval(data_result)
print precision2_perD
data_result.to_csv(path_NN["result_data"],encoding="shift-jis")

neu2.resultplot(precision_perD2, precision2_perD, Ddummy2)
