# -*- coding: utf-8 -*-
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
import datetime
import numpy as np
from numpy import NaN
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from Ssum import SVD
from count import Count
from pybrain.optimization.populationbased.ga import GA
import math
import pickle

class Neural:
    def __init__(self, data_expclass):
        self.data_expclass = data_expclass
        #self.data_expclass = data_expclass[data_expclass[u"名詞クラス"].notnull()]
        self.data_expclass.reset_index(inplace=True)
        del self.data_expclass[u'Unnamed: 0']
        del self.data_expclass[u'index']
        self.data_oversam = self.data_expclass[self.data_expclass[u'深層格'].isnull()]


    #オーバーサンプリングするメソッド
    def oversample(self):
        maxtmp = 0
        for i in self.data_expclass[u'深層格'].unique():
            if maxtmp < len(self.data_expclass[self.data_expclass[u'深層格']==i][u'深層格']):
                maxtmp = len(self.data_expclass[self.data_expclass[u'深層格']==i][u'深層格'])
        Number_per = (maxtmp/(10**int(math.log10(maxtmp))))*(10**int(math.log10(maxtmp)))
        #data_oversam = self.data_expclass[self.data_expclass[u'深層格'].isnull()]
        for i in self.data_expclass[u'深層格'].unique():
            tmpframe= self.data_expclass[self.data_expclass[u'深層格']==i]
            tmpframe.reset_index(inplace=True)
            del tmpframe[u'index']
            sampler = np.random.permutation(len(tmpframe))
            shou = Number_per/len(tmpframe[u'深層格'])
            amari = Number_per%len(tmpframe[u'深層格'])
            for j in range(shou):
                print i,j
                self.data_oversam = pd.concat([self.data_oversam,tmpframe])
            self.data_oversam = pd.concat([self.data_oversam,tmpframe.take(sampler[:amari])])
            self.data_oversam.reset_index(inplace=True)
            del self.data_oversam[u'index']
            print maxtmp
    #オーバーサンプリングするメソッド
    def oversam_perD(self, str):
        jouN=len(self.data_expclass[self.data_expclass[u'深層格']!=str])/len(self.data_expclass[self.data_expclass[u'深層格']==str])
        amari=len(self.data_expclass[self.data_expclass[u'深層格']!=str])%len(self.data_expclass[self.data_expclass[u'深層格']==str])
        sampler = np.random.permutation(len(self.data_expclass[self.data_expclass[u'深層格']==str]))
        self.data_oversam = self.data_oversam.append(self.data_expclass[self.data_expclass[u'深層格']==str].take(sampler[:amari]))

        for i in range(jouN):
            self.data_oversam = self.data_oversam.append(self.data_expclass[self.data_expclass[u'深層格']==str])

        tmp= self.data_expclass[self.data_expclass[u'深層格']!=str]
        self.data_oversam =self.data_oversam.append(tmp)

        self.data_oversam.reset_index(inplace=True)
        del self.data_oversam[u'index']

    #第一引数と第二引数の共起頻度行列を作成及び特異値分解するメソッド
    def word_vector(self, strx, stry):
        NVframe = DataFrame(self.data_oversam,columns=[strx, stry])
        NVframe[u'case']= NVframe[strx]+'_'+NVframe[stry]
        casecounts = NVframe[u'case'].value_counts()
        NVframe = NVframe.reset_index()
        del NVframe[u'index']
        Count_ob = Count()
        count = Count_ob.casecount(NVframe, casecounts)
        NVframe[u'count']= count
        NVframe = NVframe[NVframe[u'case'].notnull()]
        NVframe = NVframe.drop_duplicates()
        NVframe=NVframe.set_index([strx, stry])
        del NVframe[u'case']
        NVframe = NVframe.unstack()
        NVframe = NVframe.fillna(0)
        NVframe.columns = NVframe.columns.get_level_values(1)
        NVframe = NVframe.div(NVframe.sum(1),axis=0)
        #NVframeが共起頻度行列
        #標準化処理
        SVD_ob = SVD()
        Uframe,Vframe,Sframe = SVD_ob.SVD_run(NVframe)
        Sframe.plot()
        plt.plot( Sframe, 'o')
        #print Sframe
        #print Vframe
        m = Uframe.mean(0)
        s = Uframe.std(0)
        nd = Uframe
        nd = Uframe.sub(m,axis=1).div(s,axis=1)
        SN = SVD_ob.sf(Sframe)
        return nd, SN
    #名詞、動詞、助詞をダミー変数化するメソッド
    def dummy(self):
        Ndummy = pd.get_dummies(self.data_oversam[u"名詞クラス"])
        Vdummy = pd.get_dummies(self.data_oversam[u"動詞クラス"])
        Pdummy = pd.get_dummies(self.data_oversam[u"助詞"])
        Ddummy = pd.get_dummies(self.data_oversam[u"深層格"])
        '''
        Ndummy = self.input_flag(Ndummy)
        Vdummy = self.input_flag(Vdummy)
        Pdummy = self.input_flag(Pdummy)
        '''
        dummylist =[Ndummy,Vdummy, Pdummy]

        return dummylist, Ddummy

    def input_flag(self,dummy):
        for list in dummy:
            dummy.ix[dummy[list]==0.0, list] = -1.0
        return dummy

    #ニューラルネットワークの構造の設定と学習デーたの用意、第1~3引数を入力、第4引数を出力
    def neural_data(self, Ndummy, Vdummy, Pdummy, Ddummy):
    #def neural_data(self, Xvector, XS, Ndummy, Vdummy, Pdummy, Ddummy):
        '''
        #入力にベクトルを使用
        net = buildNetwork(XS[0]+XS[1]+XS[2]
        , 14, len(Ddummy.columns)
        )  #引数は入力層, 隠れ層, 隠れ層, ..., 出力層のノード数

        ds = SupervisedDataSet(XS[0]+XS[1]+XS[2]
        , len(Ddummy.columns)
        )  #学習サンプル：入力2個、出力1個の意
        '''
        #入力にフラグを使用
        net = buildNetwork(len(Ndummy.columns)+len(Vdummy.columns)+len(Pdummy.columns)
        ,1 , len(Ddummy.columns)
        )  #引数は入力層, 隠れ層, 隠れ層, ..., 出力層のノード数

        ds = SupervisedDataSet(len(Ndummy.columns)+len(Vdummy.columns)+len(Pdummy.columns)
        , len(Ddummy.columns)
        )  #学習サンプル：入力2個、出力1個の意


        for i in range(len(self.data_oversam)):
            print i
            X = []
            '''
            #入力にベクトルを使用
            for j in range(XS[0]):
                    if self.data_oversam.ix[i,u'名詞クラス'] in Xvector[1].index:
                        X.append(Xvector[0].ix[self.data_oversam.ix[i,u'名詞クラス'],j])
                    else:
                        X.append(0.0)
            for j in range(XS[1]):
                    if self.data_oversam.ix[i,u'動詞クラス'] in Xvector[1].index:
                        X.append(Xvector[1].ix[self.data_oversam.ix[i,u'動詞クラス'],j])
                    else:
                        X.append(0.0)
            for j in range(XS[2]):
                    if self.data_oversam.ix[i,u'助詞'] in Xvector[2].index:
                        X.append(Xvector[2].ix[self.data_oversam.ix[i,u'助詞'],j])
                    else:
                        X.append(0.0)
            '''
            #入力にフラグを使用
            for j in Ndummy.columns:
                if j == self.data_oversam.ix[i,u'名詞クラス']:
                    X.append(1.0)
                else:
                    X.append(0.0)
            for j in Vdummy.columns:
                if j == self.data_oversam.ix[i,u'動詞クラス']:
                    X.append(1.0)
                else:
                    X.append(0.0)
            for j in Pdummy.columns:
                if j == self.data_oversam.ix[i,u'助詞']:
                    X.append(1.0)
                else:
                    X.append(0.0)


            Y = []
            for j in Ddummy:
                Y.append(Ddummy[j][i])

            ds.addSample(X,Y)
        # netが未学習ニューラルネットワーク、dsがニューラルネットワークに学習させる出力
        return net, ds
    #ニューラルネットワークの学習メソッド
    def neural_learn(self, net, ds):
        #誤差逆伝搬法
        trainer = BackpropTrainer(net, ds)
        #GA
        #trainer = GA(ds.evaluateModuleMSE, net, minimize=True)

        start_time = datetime.datetime.now()  #開始時間

        #終了条件はエラーらレートが収束
        ERROR = 1e-3
        err = 100.0  #適当に大きい数値
        num = 0  #学習回数
        tmperr = 1.0
        while(err > ERROR):
            num += 1
            err =  trainer.train()
            if num%10==0:
                if tmperr < err:
                    print num, err
                    break
                tmperr = err

            print num, err
        '''
        for i in range(0,100):

            #誤差逆伝播法
            err =  trainer.train()
            print i, err

            #GA
            net = trainer.learn(0)[0]
            print i

        '''
        finish_time = datetime.datetime.now()  #終了時間
        print "time:",(finish_time - start_time)

        return net

    def netresult(self, net, ds):
        #結果表示

        i_perD = [0.0 for i in range(len(list(ds)[0][1]))]
        j_perD = [0.0 for i in range(len(list(ds)[0][1]))]
        correct_perD = [0.0 for i in range(len(list(ds)[0][1]))]
        resultlist =[]
        correctlist = []
        for input, output in ds:
            result = net.activate(input)
            print input, output, result
            resultlist.append(list(result))
            out_max = output.tolist().index(max(output.tolist()))
            re_max = result.tolist().index(max(result.tolist()))

            i_perD[out_max] +=1.0
            j_perD[re_max] += 1.0
            if re_max == out_max:
                correct_perD[out_max] += 1.0
                correctlist.append(True)
            else:
                correctlist.append(False)

        print i_perD
        precision_perD = [NaN for i in range(len(list(ds)[0][1]))]
        for i in range(len(i_perD)):
            precision_perD[i] = correct_perD[i]/i_perD[i]

        recall_perD = [NaN for i in range(len(list(ds)[0][1]))]
        for j in range(len(j_perD)):
            recall_perD[j] = correct_perD[j] / j_perD[j]

        return precision_perD, recall_perD, resultlist, correctlist

    def neteval(self, data_result):
        data_resultF = data_result[data_result[u'correct']==False]
        data_resultF.reset_index(inplace=True)
        Ddummy = pd.get_dummies(data_resultF[u"深層格"])

        i_perD = [0.0 for i in range(len(Ddummy.columns))]
        correct_perD = [0.0 for i in range(len(Ddummy.columns))]
        for i, reslist in enumerate(data_resultF[u'result']):
            rate_max = max(reslist)
            rate_max2 = -1.0
            Di = Ddummy.ix[i,:].tolist().index(max(Ddummy.ix[i,:].tolist()))

            for rate in reslist:
                if rate_max2<rate and rate!=rate_max:
                    rate_max2=rate
            ri = reslist.index(rate_max2)
            if  ri== Di:
                correct_perD[Di] += 1.0
            i_perD[Di] +=1.0

        precision_perD = [NaN for i in range(len(Ddummy.columns))]
        for i in range(len(i_perD)):
            precision_perD[i] = correct_perD[i]/i_perD[i]
        print i_perD

        return precision_perD

    def resultplot(self, precision_perD, precision2_perD, Ddummy):

        bar_width = 0.35
        plt.bar(np.array(range(1, len(Ddummy.columns) + 1)),
                np.array(precision_perD) * np.array([100] * len(Ddummy.columns))
                , width=bar_width, color="#000000", label=u"Highest", align="center")
        plt.title("")
        # plt.xlabel("Deep cases")
        plt.ylabel(u"Precisions (%)", fontsize=30)
        plt.grid(True)
        plt.bar(np.array(range(1, len(Ddummy.columns) + 1)) + bar_width,
                np.array(precision2_perD) * np.array([100] * len(precision_perD)), color="#AAAAAA", width=bar_width,
                label=u"Second_highest", align="center")
        # plt.plot(np.array(range(1,len(Ddummy.columns)+1)), np.array(precision2_perD)*np.array([100]*len(precision_perD)), label="Precision_max2")
        # plt.plot(np.array(range(1,len(Ddummy.columns)+1)), np.array(precision2_perD)*np.array([100]*len(precision_perD)), 'o')
        plt.legend(bbox_to_anchor=(1, 1), loc='lower right', borderaxespad=0, fontsize=26)
        plt.xticks(np.array(range(1, len(Ddummy.columns) + 1)) + bar_width / 2, Ddummy.columns, fontsize=30)
