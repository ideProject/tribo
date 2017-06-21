# -*- coding: utf-8 -*-

from Treport import Treport
from Language import Language
from pandas import DataFrame, Series
from TWordclass import TWordclass
import pandas as pd
import nltk
import itertools
from collections import Counter
import math
import pickle    #事象間の類似度算出

import re
import numpy as np
import sys

class Cases_extract:
    def __init__(self, Dc):
        self.Dc = Dc
    #トリプル（名詞＋助詞＋動詞）を抽出するメソッド
    def Triple_extract(self, path):
            TR = Treport(path)      #Treportに報告書データのパスを投げる
            triplelist = {}         #辞書型のtriplelistを作る
            Mor_con = [[u"形容詞", u"助動詞", u"接続詞"], [u"連体化", u"並立助詞", u"読点", u"接続助詞"]]
            for i in range(1, TR.s.nrows):      #TR.s--報告書データ   TR.s.nrows--報告書の行数
                #if i>TR.s.nrows/2: break   #本番はこれ？もしくはbreak無しのループかも
                #if i>10: break  #実験用の小規模なループ？
                if i>1: break   #より小規模なループ

                print i

                noenc = TR.delete_unnecc(i)     #noenc--いい感じの本文
                #print TR.s.cell_value(i, 2).replace(u"-", u"")
                #print noenc
                for Sentence_id, perSen in enumerate(noenc.split(u"。")):        #Sentence_id--enumerateで作られたインクリメントが入る　perSen--。区切りの文が入る
                    # TR.s.cell_value(i, 2)
                    Lan = Language(perSen)      #考察の一文を投げてLanguageのオブジェクトを作る
                    cabocha_xml = Lan.cabocha_command()     #Lanの中のcabocha_commandを呼ぶとオブジェクトを作った際にLanguageのselfに与えられた文書がcabochaで係り受け解析されその返り値がcabocha_xmlに入る
                    chunkinfo, tokinfo, sentence_tok = Lan.chunk_structured(cabocha_xml)        #chunkinfo,tokinfo,sentence_tokにそれぞれLanguage内のchunk_structured()の返り値が入る
                                                                                                #chunkinfo--文書内の文節、単語ごとにcabochaから割り当てられる係り先などの情報が入っている  辞書型
                                                                                                #tokinfo--cabochaの構文解析で得られるような品詞やらなんやらの情報が入っている リスト型
                                                                                                #sentence_tok--単語などのまとまりがリスト形式で入っている    [('対象','設備','の'),...]
                    #triple_perR = []
                    #id_perR = []
                    for chunk in chunkinfo:
                        compnoun_tail_id = -1
                        for tok_id, tokinfo_mor in enumerate(tokinfo[int(chunk[u"id"])]):   #tok_id--enumrateのインクリメント、tokinfo_mor--
                            #print tok_id, compnoun_tail_id      #tok_id--今の単語の文節番号、compnoun_tail_id--係り先の番号
                            if tok_id <= compnoun_tail_id:      #
                                continue
                            sentence_tok_set = sentence_tok[int(chunk[u"id"])]
                            if tokinfo_mor[0]==u"名詞":
                                Noun = sentence_tok_set[tok_id]
                                compnoun_tail_id = tok_id
                                for tok_id_noun in range(tok_id+1, len(tokinfo[int(chunk[u"id"])])-1):
                                    if tokinfo[int(chunk[u"id"])][tok_id_noun][0]==u"名詞" :
                                        if sentence_tok[int(chunk[u"id"])][tok_id_noun] == u"濃度":
                                            continue
                                        Noun += sentence_tok[int(chunk[u"id"])][tok_id_noun]
                                        compnoun_tail_id = tok_id_noun
                                    else:
                                        break

                                if compnoun_tail_id+1 == len(tokinfo[int(chunk[u"id"])]):
                                    continue
                                chunk_id_from = int(chunk[u"id"])


                                for i_from in reversed(range((int(chunk["id"])+1)*-1, 0)):
                                    if int(chunkinfo[int(chunk[u"id"])+i_from]["link"])==chunk_id_from:
                                        chunk_id_from -= 1
                                        from_tail_tok = tokinfo[int(chunk[u"id"])+i_from][len(tokinfo[int(chunk[u"id"])+i_from])-1]
                                        if from_tail_tok[0] in Mor_con[0] or from_tail_tok[1] in Mor_con[1]:
                                            for sentence_tok_from in reversed(list(sentence_tok[int(chunkinfo[int(chunk[u"id"])+i_from]["id"])])):
                                                Noun = sentence_tok_from + Noun
                                        else:
                                            break
                                    else:
                                        break


                                if tokinfo[int(chunk[u"id"])][compnoun_tail_id+1][0]==u"助詞" and tokinfo[int(chunk[u"id"])][compnoun_tail_id+1][1]!=u"接続助詞":
                                    Particle = tokinfo[int(chunk[u"id"])][compnoun_tail_id+1][6]

                                    Noun_suru = u""
                                    for tok_id_link, tok_link_mor in enumerate(tokinfo[int(chunk[u"link"])]):
                                        if tok_link_mor[0]==u"名詞" and tok_link_mor[1]!=u"形容動詞語幹":
                                            Noun_suru += sentence_tok[int(chunk[u"link"])][tok_id_link]
                                            continue
                                        if tok_link_mor[0]==u"動詞" or tok_link_mor[0]==u"形容詞" or tok_link_mor[1]==u"形容動詞語幹":
                                            if tok_link_mor[1]!=u"末尾":
                                                Verb = u""
                                                if tok_link_mor[6]==u"する" or tok_link_mor[6]==u"できる":
                                                    Verb = Noun_suru+u"する"
                                                else:
                                                    Verb = tok_link_mor[6]

                                                Verb_id = int(chunk[u"link"])
                                                #数字以外を削除

                                                if isinstance(TR.s.cell_value(i, 2), float):
                                                    id_tuple = (TR.s.cell_value(i, 2), Sentence_id, Verb_id)
                                                else:
                                                    if re.search("[0-9]", TR.s.cell_value(i, 2)) is None:
                                                        id_tuple = (re.search("\d+[-]*\d+", TR.s.cell_value(i, 1)[re.search("\d+[-]*\d+", TR.s.cell_value(i, 1)).end():]).group(0).replace(u"-", u""), Sentence_id, Verb_id)
                                                    else:
                                                        id_tuple = (re.search("\d+[-]*\d+", TR.s.cell_value(i, 2)).group(0).replace(u"-", u""), Sentence_id, Verb_id)

                                                if id_tuple not in triplelist.keys():
                                                    triplelist[id_tuple] = [(Noun, Particle, Verb)]
                                                else:
                                                    triple_tmp = triplelist[id_tuple]
                                                    triple_tmp.append((Noun, Particle, Verb))
                                                    triplelist[id_tuple] = triple_tmp
                                                #print Noun, Particle, Verb, TR.s.cell_value(i, 2).replace(u"-", u""), Sentence_id, Verb_id
                                                break

            return triplelist
    #事象となりうる名詞が含まれるトリプルを抽出
    def TNoun_extract(self, tripleFrame, NV_class):
        TW = TWordclass()       #TWordclass--名詞助詞動詞がまとまっているクラス、表記揺れなどを訂正する記述もある
        unify_particle= lambda x: TW.Particle_to.get(x, x)      #lambda--無名関数、unify_particle(x)=TW.Particle_to.get(x,x)という意味、Particle_toは助詞揺らぎの矯正
        tripleFrame[u"助詞"] = tripleFrame[u"助詞"].map(unify_particle)     #map()--リストやタプルのすべての要素に対して同じ処理をする、ここではtripleFrameのすべての助詞をunify_particleを用いて表記揺れを直している
        triple_Treport = [[] for i in range(len(tripleFrame.columns) + 1)]  #tripleFrameのカラム分triple_Treportに[]を作る
        for R_id, S_id, V_id, noun, particle, verb in zip(tripleFrame[u"報告書_id"], tripleFrame[u"文_id"], tripleFrame[u"動詞_id"],
                                                     tripleFrame[u"名詞"], tripleFrame[u"助詞"], tripleFrame[u"動詞"],
                                                     ): #tripleFrameの各報告書のデータを代入している
            #if id >300: break
            #print noun, particle, verb
            print "Extracting triple_Treport:", R_id, S_id, V_id
            Lan = Language(noun)        #名詞を引数としてLanguageのオブジェクトを作る、noun--報告書id、文id、動詞idに一致するものに与えられている名詞をLanguageのselfに渡すことで次のgetMorphemeで解析を行っている
            outList = Lan.getMorpheme() #','区切りでリスト型の解析結果が返ってくる
            Mor_1 = [outList[i][1] for i in range(len(outList))]    #品詞について
            Mor_2 = [outList[i][2] for i in range(len(outList))]    #接続について

            # print "outList",outList
            # print "Mor_1",Mor_1
            # print "Mor_2",Mor_2
            # sys.exit()

            noun_comp_tmp = u""
            noun_comp = []
            noun_tail = []
            noun_Pos1 = []
            noun_Pos2 = []
            for mi, Pos in enumerate(Mor_1):    #miにインクリメント、Posにそれぞれの品詞
                if mi==len(Mor_1)-1:
                    noun_comp.append(noun_comp_tmp + outList[mi][0])
                    noun_tail.append(outList[mi][0])    #outList[mi][0]--名詞部分
                    noun_Pos1.append(outList[mi][1])    #outList[mi][0]--品詞部分
                    noun_Pos2.append(outList[mi][2])    #outList[mi][0]--接続部分
                    break
                if Pos==u"名詞":
                    if Mor_1[mi+1]==u"名詞":
                        noun_comp_tmp += outList[mi][0] #名詞ならnoun_comp_tmpに追加する
                    else:
                        noun_comp.append(noun_comp_tmp+outList[mi][0])
                        noun_tail.append(outList[mi][0])
                        noun_Pos1.append(outList[mi][1])
                        noun_Pos2.append(outList[mi][2])
                        noun_comp_tmp = u""

            # print "noun_comp",noun_comp
            # print "noun_tail",noun_tail
            # print "noun_Pos1",noun_Pos1
            # print "noun_Pos2",noun_Pos2
            # print NV_class[0][1]
            # sys.exit()

            TNneed = False  #トライボロジーに関係するものかを判断する必要があるかないか
            TVneed = False  #

            #トライボロジーに関係する名詞か判定
            for cni, nounMor in enumerate(noun_comp):   #cni--enumerateによるインクリメント、nounMor--noun_compの名詞
                if noun_Pos2[cni] == u"代名詞" :   #代名詞ならTNneedをTrue
                    TNneed = True
                    break
                if nounMor in NV_class[0].keys():   #NV_class(名詞か動詞かのクラス)のなかにあるかないか
                    noun_target = nounMor   #あるならnoun_targetに代入
                elif noun_tail[cni] in NV_class[0].keys():  #
                    noun_target = noun_tail[cni]    #
                else:
                    continue    #トライボロジーに関係がない場合は次の単語へ

                # 関係がある可能性があると判断した時
                for Nclass in NV_class[0][noun_target]:
                    if Nclass in TW.TNounclass_all: #NclassがTNounclass_all(すべて抽出する)の中にあるならTNneedをTrue
                        TNneed = True
                        break
                    elif Nclass in TW.TNounclass_Nopart.keys(): #TNounclass_Nopart(部分一致でなければ抽出)
                        TNneed = True
                        for TNoun_Nopart in TW.TNounclass_Nopart[Nclass]:
                            if TNoun_Nopart in noun_target: #NV_classの中にあるものなら
                                TNneed = False

                            elif Nclass==u"様相" and noun_Pos2[cni]==u"形容動詞語幹":   #この条件でもFalseにする
                                TNneed = False


                    elif Nclass in TW.TNounclass_part.keys():   #NclassがTNounclass_part(部分一致であるなら抽出)の中にあるなら
                        for TNoun_part in TW.TNounclass_part[Nclass]:
                            if TNoun_part in noun_target:   #TNoun_partがNV_classにあるなら
                                TNneed = True
                                break
                    else:
                        continue

            #トライボロジーに関係する動詞か判定
            if TNneed:  #名詞が関係すると判定されているとき
                if verb in NV_class[1].keys():  #もし動詞がNV_classにあるとき
                    for Vclass in NV_class[1][verb]:    #
                        if Vclass in TW.TVerbclass_all:
                            TVneed = True
                            break
                        elif Vclass in TW.TVerbclass_Nopart.keys():
                            TVneed = True
                            for TVerb_Nopart in TW.TVerbclass_Nopart[Vclass]:
                                if TVerb_Nopart in verb:
                                    TVneed = False

                        elif Vclass in TW.TVerbclass_part.keys():
                            for TVerb_part in TW.TVerbclass_part[Vclass]:
                                if TVerb_part in verb:
                                    TVneed = True
                                    break
                        else:
                            continue

            if TNneed and TVneed:       #もし名詞と動詞両方がトライボロジーに関係するとき
                #並列している名詞の分解
                Mor_connect = [[u"接続詞"],[u"読点", u"並立助詞", u"接続助詞"]]
                if set(Mor_connect[0]).intersection(set(Mor_1)) or set(Mor_connect[1]).intersection(set(Mor_2)):    #set([a]).intersection(set([b]))--set[a]とset[b]の共通部分だけ出力、if文の中では共通のものがあればTure
                    noun_con = u""
                    for oi, out in enumerate(outList):  #oiにはenumrateのインクリメント、outには','区切りの解析結果
                        if outList[oi][1] not in Mor_connect[0] and outList[oi][2] not in Mor_connect[1]:
                            if out[0]!=u"等":
                                noun_con += out[0]
                        else:
                            #print out[0], noun_con
                            triple_Treport[0].append(R_id)
                            triple_Treport[1].append(S_id)
                            triple_Treport[2].append(V_id)
                            triple_Treport[3].append(noun_con)
                            triple_Treport[4].append(particle)
                            triple_Treport[5].append(verb)
                            noun_con = u""
                            continue
                        if oi==len(outList)-1:
                            triple_Treport[0].append(R_id)
                            triple_Treport[1].append(S_id)
                            triple_Treport[2].append(V_id)
                            triple_Treport[3].append(noun_con)
                            triple_Treport[4].append(particle)
                            triple_Treport[5].append(verb)
                            noun_con = u""

                else:
                    triple_Treport[0].append(R_id)
                    triple_Treport[1].append(S_id)
                    triple_Treport[2].append(V_id)
                    triple_Treport[3].append(noun)
                    triple_Treport[4].append(particle)
                    triple_Treport[5].append(verb)

        triple_Treportdict = {
            tripleFrame.columns[0]: triple_Treport[0],
            tripleFrame.columns[1]: triple_Treport[1],
            tripleFrame.columns[2]: triple_Treport[2],
            tripleFrame.columns[3]: triple_Treport[3],
            tripleFrame.columns[4]: triple_Treport[4],
            tripleFrame.columns[5]: triple_Treport[5],

        }
        tripleFrame_Treport = DataFrame(triple_Treportdict,
                                        columns=[i for i in tripleFrame.columns])

        fvu = lambda x: TW.Verb_unify.get(x, x)
        tripleFrame_Treport[u"動詞"] = tripleFrame_Treport[u"動詞"].map(fvu)
        return tripleFrame_Treport      #いろいろ精査してtripleFrame_Treportを返す

    #格フレームの抽出
    def create_caseframe(self, tripleFrame_Treport):
        Result_input = []
        Result_output = []

        DeepCase_Noun_perV = [[] for i in range(len(self.Dc.DeepCaseList) + 1)] #DeepCaseList分の[]を作る
        # SurfaceCase_Noun_perV = [[] for i in range(len(Dc.dummylist[2].columns)+1)]

        DeepCase_Noun = [[] for i in range(len(self.Dc.DeepCaseList) + 1)]  #DeepCaseList分の[]を作る
        # SurfaceCase_Noun = [[] for i in range(len(Dc.dummylist[2].columns)+1)]
        Verb_target = []
        Verb_target_id = []
        for Report_id in tripleFrame_Treport[u"報告書_id"].drop_duplicates():  #drop_duplicates--重複しているものは削除
            tripleFrame_Treport_sort = tripleFrame_Treport.ix[tripleFrame_Treport[u"報告書_id"] == Report_id,      #dataframe.ix[]--index、column両方を指定して検索ができる
                                       :].sort_index(by=[u"文_id", u"動詞_id"])                                    #今回は報告書idがfor文の変数と同じものを指定している。
            for SV_id in Series(
                    zip(tripleFrame_Treport_sort[u"文_id"], tripleFrame_Treport_sort[u"動詞_id"])).drop_duplicates():  #tripleFrame_Treport_sortの文idと動詞idを同時にfor文で回している
                for index_perF, triple_perF in enumerate(tripleFrame_Treport_sort[
                                                                     (tripleFrame_Treport_sort[u"文_id"] == SV_id[0]) & (
                                                                 tripleFrame_Treport_sort[u"動詞_id"] == SV_id[1])].loc[:,
                                                         [u"名詞", u"助詞", u"動詞"]].values):
                    Noun = triple_perF[0]
                    Particle = triple_perF[1]
                    Verb = triple_perF[2]
                    if Noun != Noun:
                        print Noun
                        continue
                    print Report_id, SV_id[0], SV_id[1]     #Report_id--報告書id、SV_id[0]--文_id、SV_id[1]--動詞_id
                    Result = self.Dc.predict(Noun, Particle, Verb)  #リスト型で、名詞や動詞とその情報が格納されたものとNNの出力値が入っている
                    DeepCase_unique = self.Dc.identify(Result)  #DeepCase_unique--深層格のどれに当たるのかをNNの値から求めている
                    # print Noun, Particle, Verb, DeepCase_unique

                    DeepCase_Noun_perV[self.Dc.DeepCaseList.index(DeepCase_unique)].append(Noun)
                    print index_perF
                    if index_perF == len(tripleFrame_Treport_sort[(tripleFrame_Treport_sort[u"文_id"] == SV_id[0]) & (
                        tripleFrame_Treport_sort[u"動詞_id"] == SV_id[1])]) - 1:
                        while [] in DeepCase_Noun_perV: #初期化かな？
                            DeepCase_Noun_perV[DeepCase_Noun_perV.index([])] = [u" "]

                        for DeepCase_Noun_tmp in list(
                                itertools.product(DeepCase_Noun_perV[0], DeepCase_Noun_perV[1], DeepCase_Noun_perV[2],
                                                  DeepCase_Noun_perV[3], DeepCase_Noun_perV[4], DeepCase_Noun_perV[5],
                                                  DeepCase_Noun_perV[6])):
                            Verb_target.append(Verb)
                            Verb_target_id.append((Report_id, SV_id[0], SV_id[1]))
                            for Di in range(len(self.Dc.DeepCaseList)):
                                DeepCase_Noun[Di].append(DeepCase_Noun_tmp[Di])

                            DeepCase_Noun_perV = [[] for i in range(len(self.Dc.DeepCaseList))] #初期化？

        cf_list = [
            (u"報告書_id", [i[0] for i in Verb_target_id]), (u"文_id", [i[1] for i in Verb_target_id]),
            (u"動詞_id", [i[2] for i in Verb_target_id]), (u"動詞", Verb_target)
        ]       #報告書id、文id、動詞id、動詞のすべてを入れている

        cf_list.extend([(self.Dc.DeepCaseList[i], DeepCase_Noun[i]) for i in range(len(self.Dc.DeepCaseList))])     #cf_listの拡張
        # cf_list.extend([(Dc.dummylist[2].columns[i], SurfaceCase_Noun[i]) for i in range(len(Dc.dummylist[2].columns))])

        case_frame = dict(cf_list)      #cf_listを辞書型に

        cd_columns = [u"報告書_id", u"文_id", u"動詞_id", u"動詞"]
        cd_columns.extend([self.Dc.DeepCaseList[i] for i in range(len(self.Dc.DeepCaseList))])  #深層格の種類も入れている
        #cd_columns--[u'報告書_id', u'文_id', u'動詞_id', u'動詞', u'主体', u'起点', u'対象', u'状況', u'着点', u'手段', u'関係']

        # cd_columns.extend([Dc.dummylist[2].columns[i] for i in range(len(Dc.dummylist[2].columns))])

        case_df = DataFrame(case_frame, columns=cd_columns)     #上二つで作ったものを一つにまとめようとしている
        case_df[u"事象"] = case_df[u"主体"] + " " + case_df[u"起点"] + " " + case_df[u"対象"] + " " + case_df[u"状況"] + " " + \
                         case_df[u"着点"] + " " + case_df[u"手段"] + " " + case_df[u"関係"] + " " + case_df[u"動詞"]
        for i in case_df.index:
            case_df.ix[i, u"事象"] = re.sub(r" +", u" ", case_df.ix[i, u"事象"].strip())

        case_df.sort_index(by=[u"報告書_id", u"文_id", u"動詞_id"], inplace=True)

        # case_df[u"報告書_id"] = [int(i) for i in case_df[u"報告書_id"]]
        return case_df
    #重み付けを行うために語句を抽出
    def extract_terms(self, case_df):
        Noun_comp = u""
        wakachi = u""
        preR_id = 1
        terms = []
        documents = []
        for (Report_id, frame) in zip(case_df[u"報告書_id"], case_df.loc[:, [u"主体", u"起点", u"対象", u"状況", u"着点", u"手段", u"関係", u"動詞"]].values):
            #if Report_id>100:break
            if preR_id != Report_id:
                documents.append(wakachi)
                print Report_id
                #print wakachi
                wakachi = u""
            if frame[7][-2:] != u"する":
                wakachi += frame[7] + u" "
                if frame[7] not in terms: terms.append(frame[7])
            else:
                wakachi += frame[7][:-2] + u" "
                if frame[7][:-2] not in terms: terms.append(frame[7][:-2])
            for i in range(0, 7):
                if frame[i] == u' ':
                    continue
                Lan = Language(frame[i])
                outList = Lan.getMorpheme()
                Mor_1 = [outList[i][1] for i in range(len(outList))]
                # if (u"接続詞" in Mor_1) | (u"記号" in Mor_1):
                #    continue
                for mi, Mor in enumerate(outList):
                    if Mor_1[mi] == u"名詞" and Mor[2] != u"形容動詞語幹":
                        Noun_comp += Mor[0]
                        if mi < len(Mor_1) - 1:
                            if Mor_1[mi + 1] != u"名詞":
                                wakachi += Noun_comp + u" "
                                if Noun_comp not in terms: terms.append(Noun_comp)
                                Noun_comp = u""
                        else:
                            wakachi += Noun_comp + u" "
                            if Noun_comp not in terms: terms.append(Noun_comp)
                            Noun_comp = u""
                    elif Mor_1[mi] != u"助詞" and Mor_1[mi] != u"助動詞" and Mor[5] != u"サ変・スル" and Mor[2] != u"接尾":
                        wakachi += Mor[0] + u" "
                        if Mor[0] not in terms: terms.append(Mor[0])

            preR_id = Report_id
        documents.append(wakachi)
        return terms, documents


    #類似度の高い格フレームの統合
    def bunrui_frame(self, case_df, terms, idf_Treport, dist_method, threshould_dist):
        MorList = []
        Noun_comp = u""
        Noun_weight = 2.0       #重み
        idf_Treport = Series(idf_Treport)       #idf_Treport--リスト型だからSeries(idf_Treport)にすることでデータを扱いやすい形に変えている
        zero = min(idf_Treport)
        if zero==0:
            min_idf=1.0
            for idf in idf_Treport: #各単語ごとのidfを抜き出している
                if idf<min_idf and idf!=zero:   #idfの最小値を保持する
                    min_idf=idf
            idf_Treport[idf_Treport == 0] = min_idf*0.5     #idf_Treport[]の値が0のものをmin_idf*0.5に書き換えている


        #ここの処理で事象の単語を重みとidfを用いてそれぞれの単語に値を与えている
        for frame in case_df[u"事象"].drop_duplicates().values:   #frameにcase_dfの事象に当たる個所のvaluesを入れている
            # print "frame",frame #事象が入る
            MorList_tmp = {}
            for i, words in enumerate(frame.split(u" ")):   #frameにある単語一つずつがwordsに入る
                #print words, u":"
                # print "words",words #事象の各単語が入る
                if i==len(frame.split(u" "))-1:     #もしframe内の最後の単語をwordsが取得した時
                    if words[-2:] != u"する":
                        MorList_tmp[words] = idf_Treport[terms.index(words)]
                    else:
                        MorList_tmp[words[:-2]] = idf_Treport[terms.index(words[:-2])]
                    #エラー回避用xm
                    Noun_comp = u""
                else:
                    Lan = Language(words)       #Languageにwordsを投げる
                    outList = Lan.getMorpheme()     #mecabの処理を返してくれる(ここではwordsをmecabで解析した結果が返ってくる)
                    Mor_1 = [outList[i][1] for i in range(len(outList))]    #outList内の品詞をMor_1に取り出している

                    for mi, Mor in enumerate(outList):  #wordsの品詞ごとにMorに入る
                        # print "Mor",Mor #単語をmecabに投げた時の結果の各品詞が入る
                        # print "Mor_1",Mor_1
                        # print "MorList_tmp",MorList_tmp
                        if Mor_1[mi] == u"名詞" and Mor[2] != u"形容動詞語幹":  #Mor_1[mi]が名詞で且つ形容動詞語幹でないとき
                            Noun_comp += Mor[0] #Noun_compにその語を入れる
                            if mi < len(Mor_1) - 1: #もしMor_1のサイズ-1よりも小さなループの時
                                if Mor_1[mi + 1] != u"名詞":  #もしMor_1[mi + 1]が名詞でないとき
                                    #ここの上二つの条件によって例えば『フィルタ表面』など複合的な名詞も分かれて保持するのではなく同じ名詞として扱うことができる
                                    MorList_tmp[Noun_comp] = idf_Treport[terms.index(Noun_comp)] * Noun_weight  #MorList_tmpにNoun_compというkeyの辞書項目を作り、そのvaluesに抽出した単語リストの番号にあたるidf_Treportのidfに重みをかけた値を入れる
                                    Noun_comp = u""

                            else:   #Mor_1の最後を参照した時
                                MorList_tmp[Noun_comp] = idf_Treport[terms.index(Noun_comp)] * Noun_weight
                                Noun_comp = u""
                        elif Mor_1[mi] != u"助詞" and Mor_1[mi] != u"助動詞" and Mor[5] != u"サ変・スル" and Mor[2] != u"接尾": #Mor_1[mi]が助詞且つ助動詞且つサ変・スル且つ接尾でないとき
                            #print Mor[0]
                            # print "Mor_1[mi]",Mor_1[mi]
                            MorList_tmp[Mor[0]] = idf_Treport[terms.index(Mor[0])]

            MorList.append(MorList_tmp) #事象ごとにMorList_tmp（単語ごとに重みによって与えた値を入れている）をappendしている
        print "MorList",MorList #MorList--うえで処理した事象ごとに辞書が設けられ、その辞書内では各単語ごとに重みとidfによって与えられた値が保持されている


        #caseFrame = case_df[u"主体"] + u" " + case_df[u"起点"] + u" " + case_df[u"対象"] + u" " + case_df[u"状況"] + u" " + case_df[
         #   u"着点"] + u" " + case_df[u"手段"] + u" " + case_df[u"関係"] + u" " + case_df[u"動詞"]
        cf = [i for i in case_df[u"事象"].drop_duplicates()]      #cfにはただcase_df内の事象が重複せずに入っている


        #Jaccard係数による統一辞書の作成
        Wdist_index = []
        Wdist_column = []
        Wdist = []
        unifyList = {}
        Case_freq = Counter(case_df[u"事象"])
        # 各文の動詞が反対語リストに含まれていれば分類しない
        oppositeList = [u"良好", u"正常", u"低下"]

        print len(cf), len(MorList)
        for i, x in enumerate(MorList): #i--enumerateのインクリメント、x--MorListの各単語に対する値の辞書型が入る
            print u"calculating distance... ", i
            x_keys_set = set(x.keys())  #xの単語のほうが入る
            for j, y in enumerate(MorList[i + 1:]): #j--enumerateのインクリメント、y--MorListの最初の事象の次の事象をyに入れている
                #xの次以降の事象がyということになる。
                j = i + j + 1
                y_keys_set = set(y.keys())  #yの単語のほうが入る
                # print j
                if bool(set(oppositeList).intersection(x_keys_set)) and not(bool(y_keys_set.issuperset(set(oppositeList).intersection(x_keys_set)))):   #oppositeList(反対語リスト)とx_keys_setが一致する、またoppositeListとx_keys_setが一致している単語それ以上の値を示していないとき.s.issuperset(t)--s >= t
                    continue
                elif bool(set(oppositeList).intersection(y_keys_set)) and not(bool(x_keys_set.issuperset(set(oppositeList).intersection(y_keys_set)))): #oppositeList(反対語リスト)とy_keys_setが一致する、またoppositeListとy_keys_setが一致している単語それ以上の値を示していないとき.s.issuperset(t)--s >= t
                    continue

                if (x.keys() in unifyList.keys()) | (y.keys() in unifyList.keys()): #y.keysもしくはx.keysがunifyList.keysに含まれているとき
                    continue

                if bool(x_keys_set.intersection(y_keys_set)) and cf[i] != cf[j]:    #x_keys_setとy_keys_setで一致するものがあるとき且つ、i番目とj番目の事象が一致しないとき

                    sym = x_keys_set.symmetric_difference(y_keys_set)   #s.symmetric_difference(t)--s^t(sとtのどちらか一方だけに属する要素からなる集合),この場合x_keys_setとy_keys_setのどちらか一方だけに属しているものの集合が格納されている
                    print "sym",sym,len(sym)
                    if len(sym)>3:
                        continue
                    #排他的論理和形態素に名詞が（２つ以上）含まれていてはいけない(時間かかる)
                    '''
                    Mor_sd = [(Language(sdm).getMorpheme().pop()[1], Language(sdm).getMorpheme().pop()[2]) for sdm in sym]

                    for Mor_set in [(u"名詞", u"サ変接続"), (u"名詞", u"形容動詞語幹")]:
                        while Mor_set in Mor_sd:
                            Mor_sd.remove(Mor_set)

                    if [ms[0] for ms in Mor_sd].count(u"名詞")<2:
                    '''
                    xy_set = dict(x.items() + y.items())    #xとyのkeys,valuesすべてを辞書型で入れている。itemsを使うと(keys,values)のタプル型が取得できる
                    xy_insec = x_keys_set.intersection(y_keys_set)  #x_keys_setとy_keys_setで同じ値があるもの
                    w_all = 0.00    #これが類似度の値？
                    #↓ここで引数で指定した類似度の求め方を実行している
                    if dist_method == u"Jaccard":
                        #jaccard係数
                        for mor_val in xy_set.values():
                            w_all += mor_val
                    elif dist_method == u"Simpson":
                        #Simpthon係数
                        if len(x.keys())<len(y.keys()):
                            for mor_val in x.values():
                                w_all += mor_val
                        else:
                            for mor_val in y.values():
                                w_all += mor_val

                    w_insec = 0.00
                    for mor_val in xy_insec:    #xy_insec--x_keys_set,y_keys_setで同じ値があるものの集合、mor_valはそれを一つずつ受け取る
                        print "xy_set[mor_val]",xy_set[mor_val]
                        w_insec += xy_set[mor_val]  #w_insecでは上で求めた値が加算されていく
                    dist_str = w_insec / w_all  #上で求めたものの比を表している？

                    if dist_str >= threshould_dist: #dist_strが閾値より高いとき
                        '''
                        if dist_method==u"Jaccard":
                            #頻度が高い格フレームに統一
                            if Case_freq[cf[j]] <= Case_freq[cf[i]] and cf[i] not in unifyList.keys():
                                unifyList[cf[i]] = cf[j]
                            elif Case_freq[cf[j]] > Case_freq[cf[i]] and cf[j] not in unifyList.keys():
                                unifyList[cf[j]] = cf[i]

                        elif dist_method==u"Simpson":
                        '''
                        #形態素数が少ない格フレームに統一
                        if len(x_keys_set) < len(y_keys_set) and cf[j] not in unifyList.keys():
                            unifyList[cf[j]] = cf[i]
                        elif len(x_keys_set) > len(y_keys_set) and cf[i] not in unifyList.keys():
                            unifyList[cf[i]] = cf[j]
                        elif len(cf[i])<len(cf[j]) and cf[j] not in unifyList.keys():
                            unifyList[cf[j]] = cf[i]
                        elif len(cf[i])>=len(cf[j]) and cf[i] not in unifyList.keys():
                            unifyList[cf[i]] = cf[j]
                        #print "%d:%s" % (i, cf[i]), "%d:%s" % (j, cf[j]), dist_str, w_insec, w_all
                        #print outList[len(outList) - 1][0], outList[len(outList) - 1][1], outList[len(outList) - 1][2]
                        Wdist_index.append(cf[i])
                        Wdist_column.append(cf[j])
                        Wdist.append(dist_str)

        print "Wdist",Wdist
        Wdist = DataFrame(Wdist, index=[Wdist_index, Wdist_column], columns=[u"Similarity"])    #統一し終わったものをDataFrame型に変換
        print "Wdist",Wdist     #DataFrame型にWdistを変えている。中身としては、事象A  事象B　Similarityって感じ
        print "unifyList",unifyList #統一が発生した時、条件に応じて　事象A:事象B　って感じで辞書型に格納される
        print "Wdist_index",Wdist_index #Wdistの左側の事象
        print "Wdist_column",Wdist_column   #Wdistの右側の事象
        fnc = lambda x: unifyList.get(x, x)
        insecset = set()
        while set(case_df[u"事象"]).intersection(set(unifyList.keys())):  #case_df[u"事象"]とunifyList.keys()が一致するとき
            if insecset== set(case_df[u"事象"]).intersection(set(unifyList.keys())):  #この条件だと絶対１週しかしなさそうだし違う条件分岐でもよくない？って思った。ただ最初からbreakすることもあるのかもしれないので何とも言えない
                break
            case_df[u"事象"] = case_df[u"事象"].map(fnc)    #unifyListに該当するものがあったら補完しているのかも？よくわからない
            insecset = set(case_df[u"事象"]).intersection(set(unifyList.keys()))
        return case_df, Wdist   #事象を重複せずにまとめてunifyListを噛ませたcase_dfと事象間のSimilarityを求めてあるWdistが返される

    #ゼロ代名詞が含まれると判断するニューラルネットワークの出力の閾値の算出
    def Cal_thresold(self, case_df, output_thresold):
        NNoutputList = []
        for Report_id in case_df[u"報告書_id"].drop_duplicates():
            print u"Calculating thresold:", Report_id
            case_df_perR = case_df[case_df[u"報告書_id"] == Report_id]     #報告書idごとにそれぞれのidや深層格などを抜き出している

            for first_Sen, Sentence_id in enumerate(case_df_perR[u"文_id"].drop_duplicates()):   #報告書idごとに出現している文idを抜き出している
                for line in case_df_perR[case_df[u"文_id"] == Sentence_id].iterrows():
                    """     lineこんな感じ
                    報告書_id    108003794
                    文_id              0
                    動詞_id            12
                    動詞              受ける
                    主体                 
                    起点                 
                    対象            沈降の影響
                    状況                 
                    着点                 
                    手段                 
                    関係                 
                    事象        沈降の影響 受ける
                    Name: 0, dtype: object)
                    """
                    for di, l in enumerate(line[1][4:11].values):       #line内の動詞～事象のvaluesを指定している
                        if l != u" ":       #深層格に何か入っていたら
                            NNoutputList.append([i[1] for i in self.Dc.predict(l, u"", line[1][3])])    #line[1][3]--動詞、predict(深層格予測)に(名詞、u""、動詞)を送る
        maxList_perD = [[] for i in range(0, 7)]
        thresold_perD = [[] for i in range(0, 7)]
        for perline in NNoutputList:    #NNoutputList(リスト型)から一つのリストを取り出す
            for out_perline in perline: #そのリストから一文字目を取り出す
                maxList_perD[out_perline.index(max(out_perline))].append(max(out_perline))      #出力値が最大の深層格の場所(index)に値(max(out_perline))を入れている

        while [] in maxList_perD:
            maxList_perD[maxList_perD.index([])] = [0.0]
        for i, mlp in enumerate(maxList_perD):
            thresold_perD[i] = np.percentile(np.array(mlp), output_thresold)
        return maxList_perD, thresold_perD

    #因果連鎖分割（因果連鎖番号の割り当て）
    def Section_div(self, case_df, VC_Dc, thresold_perD):   #case_df--設備クラスタ、VC_Dc--共起頻度、thresold_preD--閾値
        Record_id = dict()  # 文_id:レコード_id
        Record_id[(case_df.ix[0, :][u"報告書_id"], case_df.ix[0, :][u"文_id"])] = 0     #Record_idの初期化
        tail_key = -1
        before_list = []
        after_list = []
        Report_id_list = []
        Sentence_id_list = []
        for Report_id in case_df[u"報告書_id"].drop_duplicates():      #Report_idに報告書idが入る
            print u"Extracting SecN_id:", Report_id
            Noun_pre = dict()       #Noun_preの初期化、報告書ごとの名詞の一覧
            # print Report_id
            case_df_perR = case_df[case_df[u"報告書_id"] == Report_id]     #case_df_perR--抜き出したReport_idと一致する報告書(case_df)のリストが入る、データとしては報告書id、文id、動詞id、動詞、深層格が入る
            for first_Sen, Sentence_id in enumerate(case_df_perR[u"文_id"].drop_duplicates()):       #case_df_perRの文idが入る
                # print "first_Sen",first_Sen
                for line in case_df_perR[case_df[u"文_id"] == Sentence_id].iterrows():       #文idがcase_df_perRと一致するリストを抜き出してlineに入れる。lineは各事象ごとの動詞や深層格の情報が入っている。
                    # print "line[1][1]",line[1][1]   #文id
                    # print "Noun_pre",Noun_pre   #{0L: [u'沈降の影響', u'濃度'], 2L: [u'μm以下の疲労摩耗粒子', u'軸受の寿命の指標'], 4L: [u'リン', u'使用油である日石タービン']}って感じで入る。0Lとかの0は文id、各文ごとの名詞が文idと共に辞書型として格納されている

                    # print line[1][3]
                    if line[1][1] not in Noun_pre.keys():   #line[1][1]--文id、がNoun_preのkeyにないとき。最初はこの条件を満たして処理を行い、それ以降はelseの方に行くかな？
                        Noun_pre[line[1][1]] = [l for l in line[1][4:11].values if l != u" "]   #深層格の中にある名詞が入る
                    else:
                        Noun_pre[line[1][1]] = Noun_pre[line[1][1]] + [l for l in line[1][4:11].values if l != u" "]    #既存のNoun_preに新たにlineの深層格内にある名詞のリストを追加する
                    # 代名詞の補完
                    for di, l in enumerate(line[1][4:11].values):       #line[1][4:11]--深層格に割り当てられている名詞がlに入る    例）l = "沈降の影響"
                        # print "di",di
                        if l != u" ":   #深層格が割り当てられているとき
                            Lan = Language(l)   #深層格が割り当てられている名詞lをLanguageに投げる
                            outList = Lan.getMorpheme() #上で投げた名詞のmecabによる解析結果をoutListに入れる
                            if set([u"代名詞"]).intersection(set([outList[i][2] for i in range(len(outList))])):   #set([a]).intersection(set([b]))--set[a]とset[b]の共通部分だけ出力、if文の中では共通のものがあればTure
                                                                                                                    #mecabで処理を行い代名詞があるとわかった時の条件分岐.代名詞を含んだひとまとまりの事象の時も入る
                                # '''       ↓謎
                                #代名詞の出力ベクトルと名詞の出力ベクトルのユークリッド距離が最小の名詞を選択
                                pronoun_vec = [np.array(out_perD[1]) for out_perD in self.Dc.predict(l, u"", line[1][3]) if #Dc.predict(名詞、助詞、動詞)だからline[1][3]は動詞
                                               np.argmax(np.array(out_perD[1])) == di]  #argmax([A])--[A]の中で最大値を持つインデックスを取得、たぶんifの条件は深層格に複数名詞が割り当てられているときにほしいデータの結果のみを得ようとしている
                                if len(pronoun_vec) == 0:   #pronoun_vecに何も入っていないとき
                                    pronoun_vec = [np.array(out_perD[1]) for out_perD in self.Dc.predict(l, u"", line[1][3])]
                                print "pronoun_vec", pronoun_vec  # pronoun_vec--例）[array([ 0.00528617, -0.00143269,  0.81343152,  0.02207774,  0.12166978,0.01644565,  0.02252184])]って感じ。各深層格に対する帰属度が格納される？
                                Noun_out = [
                                    {Np: [np.array(output[1]) for output in self.Dc.predict(Np, u"", line[1][3])] for Np in
                                     Np_list if Np not in line[1][4:11].values} for Np_list in
                                    [Noun_pre[line[1][1] - pre_i] for pre_i in range(0, 2) if
                                     line[1][1] - pre_i in Noun_pre.keys()]]
                                if len(Noun_out[0]) == 0:   #何も入ってなかったら消す
                                    del Noun_out[0]
                                if len(Noun_out) == 0:  #Noun_outにまだ事象がないならbreak
                                    break

                                Neuclid_perS = [
                                    {n: min([np.linalg.norm(pv - vec) for vec in No[n] for pv in pronoun_vec]) for n in
                                     No.keys()} for No in Noun_out]
                                Neuclid_min_perS = [(perS.keys()[perS.values().index(min(perS.values()))], min(perS.values())) for perS in Neuclid_perS]
                                toNoun = [N_ed[0] for N_ed in Neuclid_min_perS if
                                          min([nmp[1] for nmp in Neuclid_min_perS]) == N_ed[1]]
                                case_df.ix[line[0], u"事象"] = case_df.ix[line[0], u"事象"].replace(l, toNoun[0])
                                # print "toNoun[0]",toNoun[0] #ユークリッド距離が一番小さな名詞、代名詞を置き換える用
                                print "before:Noun_pre",Noun_pre
                                Noun_pre[line[1][1]][Noun_pre[line[1][1]].index(l)] = toNoun[0]     #ここで"これ"とかの代名詞をtoNoun[0]で補完している
                                # print "Neuclid_perS",Neuclid_perS   #報告書ごとに深層格に割り当てられた名詞のユークリッド距離を求めている   ユークリッド距離が一番短いものが代名詞補完に使われて要るっぽい
                                # print "Neuclid_min_perS", Neuclid_min_perS  #求められたユークリッド距離から最小なものを抽出している
                                print "after:Noun_pre", Noun_pre
                            # '''

                                '''
                                #深層格における最大出力である名詞を選択
                                Noun_out = [{Np: max([output[1][di] for output in self.self.Dc.predict(Np, u"", line[1][3])]) for Np in Np_list if Np not in line[1][4:11].values} for Np_list in [Noun_pre[line[1][1] - pre_i] for pre_i in range(0, 2) if
                                                              line[1][1] - pre_i in Noun_pre.keys()]]
                                #del Noun_out[0][l]
                                if len(Noun_out[0])==0:
                                    del Noun_out[0]
                                if len(Noun_out)==0:
                                    break
                                MaxN_perS = [No[No.keys()[No.values().index(max(No.values()))]] for No in Noun_out]
                                SSen_rec = MaxN_perS.index(max(MaxN_perS))
                                toNoun = Noun_out[SSen_rec].keys()[Noun_out[SSen_rec].values().index(max(MaxN_perS))]
                                case_df.ix[line[0], u"事象"] = case_df.ix[line[0], u"事象"].replace(l, toNoun)
                                Noun_pre[line[1][1]][Noun_pre[line[1][1]].index(l)] = toNoun
                                '''

                    # 埋まっていない深層格（ゼロ代名詞）の補完
                    Deep_cand = []
                    for i in [VC_Dc[VC] for VC in self.Dc.NV_class[1][line[1][3]] if VC in VC_Dc]:  #VC_Dc--分類語彙表と動詞項構造シソーラスの共起頻度、NV_class--動詞か名詞のクラス、NV_class[1][line[1][3]]で動詞を取り出してVC_DcにあればVC_Dcにおけるそのリストをiに入れる
                        Deep_cand += i      #[u'対象', u'関係', u'対象', u'着点']こんな感じで動詞の深層格が入る
                    # print "Deep_cand",Deep_cand
                    Count_perD = [Deep_cand.count(d) for d in self.Dc.DeepCaseList]     #self.Dc.DeepCaseList--[u'主体', u'起点', u'対象', u'状況', u'着点', u'手段', u'関係']
                    # print "Count_perD",Count_perD   #Deep_candに含まれる深層格が[u'主体', u'起点', u'対象', u'状況', u'着点', u'手段', u'関係']の形でいくつ現れているのかをカウントしている。例）[0, 0, 2, 0, 1, 0, 1]
                    Dc_toV = [Deep_cor for Deep_cor in
                              [d for d, Deep_cor in zip(self.Dc.DeepCaseList, Count_perD) if
                               sum(Count_perD) / float(len(Count_perD)) < Deep_cor]]
                    # print "Dc_toV",Dc_toV   #Dc_toV [u'対象', u'着点', u'関係']こんな感じ  もしかしたらここで出てくる奴はゼロ代名詞があると判断された深層格が出てるのかも
                    # print "line",line
                    Noun_zero = dict()
                    for Dc_tmp in Dc_toV:
                        if line[1][Dc_tmp] == u" ":     #Dc_toVで出た深層格が埋まっていないとき
                            Noun_out = [{Np: max([output[1][self.Dc.DeepCaseList.index(Dc_tmp)] for output in self.Dc.predict(Np, u"", line[1][3])]) for Np in Np_list if Np not in line[1][4:11].values} for Np_list in [Noun_pre[line[1][1] - pre_i] for pre_i in range(0, 2) if
                                                    line[1][1] - pre_i in Noun_pre.keys()]] #Noun_out--入る可能性がある名詞とその帰属度が辞書型で格納されている。
                            while {} in Noun_out:   #Noun_outのいらない部分である{}を消して整理している
                                Noun_out.remove({})
                            if len(Noun_out) == 0:  #整理した結果何もなかったらループやり直し
                                continue
                            MaxN_perS = [No[No.keys()[No.values().index(max(No.values()))]] for No in   #NoにはNoun_out内にある名詞とその帰属度の辞書型が入る。
                                         Noun_out]
                            SSen_rec = MaxN_perS.index(max(MaxN_perS))  #SSen_rec--MaxN_perSの中で一番大きな値を持っているインデックスを保持する
                            if max(MaxN_perS) > thresold_perD[self.Dc.DeepCaseList.index(Dc_tmp)]:  #もしMaxN_perSがそれぞれの深層格ごとに求めた閾値thresold_perDよりも大きければ
                                Noun_zero[Dc_tmp] = Noun_out[SSen_rec].keys()[Noun_out[SSen_rec].values().index(max(MaxN_perS))]
                                # print "Noun_zero[Dc_tmp]",Noun_zero[Dc_tmp]
                    if len(Noun_zero.keys()) > 0:   #Noun_zero.keys()に何かが入っているとき
                        case_zero = u"" #case_zeroを初期化
                        for d, Noun_perD in zip(line[1][4:11].keys(), line[1][4:11].values):    #dに深層格、Noun_perDにその深層格に割り当てられている単語が入る
                            if d in Noun_zero.keys():   #もしdがNoun_zero.keys()に含まれているとき、Noun_zeroにはkeysに深層格が、valuesにその格の名詞が含まれている
                                case_zero += u" " + Noun_zero[d]    #case_zeroに名詞を加算
                            else:
                                case_zero += u" " + Noun_perD   #dの格にある名詞を加算

                        case_zero += u" " + line[1][3]
                        case_zero = re.sub(r" +", u" ", case_zero.strip())      #ゼロ代名詞を補完した事象が入る

                        #'''追加部分
                        before_list.append(line[1][11])
                        after_list.append(case_zero)
                        Report_id_list.append(Report_id)
                        Sentence_id_list.append(Sentence_id)
                        #'''

                        case_df.ix[line[0], u"事象"] = case_zero
                        for Noun_zero_tmp in Noun_zero.values():
                            Noun_pre[line[1][1]].append(Noun_zero_tmp)  #ゼロ代名詞が加わったNoun_preになっている

                # 前の文に含まれる名詞が含まれているか
                if first_Sen == 0 and tail_key != -1:   #最初の文は前の文とかがないからこの条件に入ってcontinue
                    Record_id[(Report_id, Sentence_id)] = Record_id[tail_key] + 1
                    continue
                for pre_i in range(3, 0, -1):   #range(start,stop,step)--今回の場合、3から-1ずつ変化して0になるまでってこと
                    if line[1][1] - pre_i in Noun_pre.keys():   #line[1][1]は文id、つまり文id-pre_i（３～０）の範囲にNoun_pre.keys()、ゼロ代名詞を補完した名詞が含まれているとき。先行研究ではrange(3.0.-1)と3文前までに名詞が含まれているのかを見ている？
                        if set(Noun_pre[line[1][1]]).intersection(set(Noun_pre[line[1][1] - pre_i])):   #前の文章に同じ名詞が出ているなら
                            for pre_j in range(pre_i, -1, -1):
                                if line[1][1] - pre_j in Noun_pre.keys():   #報告書の名詞リストの中にあったら
                                    Record_id[(Report_id, Sentence_id - pre_j)] = Record_id[
                                        (Report_id, line[1][1] - pre_i)]        #Record_idは報告書id,文idがどこにかかっているのかを表している?因果連鎖っぽいかも？

                            break
                        else:
                            Record_id[(Report_id, Sentence_id)] = Record_id[(Report_id, line[1][1] - pre_i)] + 1    #前の文とつながっていることにする
                while (Report_id, Sentence_id) not in Record_id.keys(): #ここで新しい辞書型を作る
                    pre_i += 1
                    if (Report_id, Sentence_id - pre_i) in Record_id.keys():
                        Record_id[(Report_id, Sentence_id)] = Record_id[(Report_id, line[1][1] - pre_i)] + 1
                if first_Sen == len(case_df_perR[u"文_id"].drop_duplicates()) - 1:
                    tail_key = (Report_id, Sentence_id)     #何かに使っているかと思ったけど一番最初の文なのかどうかを判断するためくらいしか使ってなさそう？

        # '''追加部分
        list_dataframe = pd.DataFrame({})
        list_dataframe['Report_id'] = Report_id_list
        list_dataframe['Sentence_id'] = Sentence_id_list
        list_dataframe['before_id'] = before_list
        list_dataframe['after_id'] = after_list
        print list_dataframe
        list_dataframe.to_csv("data/hokan.csv", encoding='shift-jis', index=False)
        # '''


        case_df[u"レコード_id"] = [(i, j) for i, j in zip(case_df[u"報告書_id"], case_df[u"文_id"])]
        case_df[u"レコード_id"] = case_df[u"レコード_id"].map(lambda x: Record_id[x])



        return case_df


