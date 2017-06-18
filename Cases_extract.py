# -*- coding: utf-8 -*-
###
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

class Cases_extract:
    def __init__(self, Dc):
        self.Dc = Dc
    #トリプル（名詞＋助詞＋動詞）を抽出するメソッド
    def Triple_extract(self, path):
            TR = Treport(path)
            triplelist = {}
            Mor_con = [[u"形容詞", u"助動詞", u"接続詞"], [u"連体化", u"並立助詞", u"読点", u"接続助詞"]]
            for i in range(1, TR.s.nrows):
                #if i>TR.s.nrows/2: break
                #if i>5: break
                print i

                noenc = TR.delete_unnecc(i)
                #print TR.s.cell_value(i, 2).replace(u"-", u"")
                #print noenc
                for Sentence_id, perSen in enumerate(noenc.split(u"。")):
                   # TR.s.cell_value(i, 2)
                    Lan = Language(perSen)
                    cabocha_xml = Lan.cabocha_command()
                    chunkinfo, tokinfo, sentence_tok = Lan.chunk_structured(cabocha_xml)
                    #triple_perR = []
                    #id_perR = []
                    for chunk in chunkinfo:
                        compnoun_tail_id = -1
                        for tok_id, tokinfo_mor in enumerate(tokinfo[int(chunk[u"id"])]):
                            #print tok_id, compnoun_tail_id
                            if tok_id <= compnoun_tail_id:
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
        TW = TWordclass()
        unify_particle= lambda x: TW.Particle_to.get(x, x)
        tripleFrame[u"助詞"] = tripleFrame[u"助詞"].map(unify_particle)
        triple_Treport = [[] for i in range(len(tripleFrame.columns) + 1)]
        for R_id, S_id, V_id, noun, particle, verb in zip(tripleFrame[u"報告書_id"], tripleFrame[u"文_id"], tripleFrame[u"動詞_id"],
                                                     tripleFrame[u"名詞"], tripleFrame[u"助詞"], tripleFrame[u"動詞"],
                                                     ):
            #if id >300: break
            #print noun, particle, verb
            print "Extracting triple_Treport:", R_id, S_id, V_id
            Lan = Language(noun)
            outList = Lan.getMorpheme()
            Mor_1 = [outList[i][1] for i in range(len(outList))]
            Mor_2 = [outList[i][2] for i in range(len(outList))]
            noun_comp_tmp = u""
            noun_comp = []
            noun_tail = []
            noun_Pos1 = []
            noun_Pos2 = []
            for mi, Pos in enumerate(Mor_1):
                if mi==len(Mor_1)-1:
                    noun_comp.append(noun_comp_tmp + outList[mi][0])
                    noun_tail.append(outList[mi][0])
                    noun_Pos1.append(outList[mi][1])
                    noun_Pos2.append(outList[mi][2])
                    break
                if Pos==u"名詞":
                    if Mor_1[mi+1]==u"名詞":
                        noun_comp_tmp += outList[mi][0]
                    else:
                        noun_comp.append(noun_comp_tmp+outList[mi][0])
                        noun_tail.append(outList[mi][0])
                        noun_Pos1.append(outList[mi][1])
                        noun_Pos2.append(outList[mi][2])
                        noun_comp_tmp = u""


            TNneed = False
            TVneed = False

            #トライボロジーに関係する名詞か判定
            for cni, nounMor in enumerate(noun_comp):
                if noun_Pos2[cni] == u"代名詞" :
                    TNneed = True
                    break
                if nounMor in NV_class[0].keys():
                    noun_target = nounMor
                elif noun_tail[cni] in NV_class[0].keys():
                    noun_target = noun_tail[cni]
                else:
                    continue

                for Nclass in NV_class[0][noun_target]:
                    if Nclass in TW.TNounclass_all:
                        TNneed = True
                        break
                    elif Nclass in TW.TNounclass_Nopart.keys():
                        TNneed = True
                        for TNoun_Nopart in TW.TNounclass_Nopart[Nclass]:
                            if TNoun_Nopart in noun_target:
                                TNneed = False

                            elif Nclass==u"様相" and noun_Pos2[cni]==u"形容動詞語幹":
                                TNneed = False


                    elif Nclass in TW.TNounclass_part.keys():
                        for TNoun_part in TW.TNounclass_part[Nclass]:
                            if TNoun_part in noun_target:
                                TNneed = True
                                break
                    else:
                        continue
            #トライボロジーに関係する動詞か判定
            if TNneed:
                if verb in NV_class[1].keys():
                    for Vclass in NV_class[1][verb]:
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

            if TNneed and TVneed:
                #並列している名詞の分解
                Mor_connect = [[u"接続詞"],[u"読点", u"並立助詞", u"接続助詞"]]
                if set(Mor_connect[0]).intersection(set(Mor_1)) or set(Mor_connect[1]).intersection(set(Mor_2)):
                    noun_con = u""
                    for oi, out in enumerate(outList):
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
        return tripleFrame_Treport

    #格フレームの抽出
    def create_caseframe(self, tripleFrame_Treport):
        Result_input = []
        Result_output = []

        DeepCase_Noun_perV = [[] for i in range(len(self.Dc.DeepCaseList) + 1)]
        # SurfaceCase_Noun_perV = [[] for i in range(len(Dc.dummylist[2].columns)+1)]

        DeepCase_Noun = [[] for i in range(len(self.Dc.DeepCaseList) + 1)]
        # SurfaceCase_Noun = [[] for i in range(len(Dc.dummylist[2].columns)+1)]
        Verb_target = []
        Verb_target_id = []
        for Report_id in tripleFrame_Treport[u"報告書_id"].drop_duplicates():
            tripleFrame_Treport_sort = tripleFrame_Treport.ix[tripleFrame_Treport[u"報告書_id"] == Report_id,
                                       :].sort_index(by=[u"文_id", u"動詞_id"])
            for SV_id in Series(
                    zip(tripleFrame_Treport_sort[u"文_id"], tripleFrame_Treport_sort[u"動詞_id"])).drop_duplicates():
                for index_perF, triple_perF in enumerate(tripleFrame_Treport_sort[
                                                                     (tripleFrame_Treport_sort[u"文_id"] == SV_id[0]) & (
                                                                 tripleFrame_Treport_sort[u"動詞_id"] == SV_id[1])].loc[:,
                                                         [u"名詞", u"助詞", u"動詞"]].values):
                    Noun = triple_perF[0]
                    Particle = triple_perF[1]
                    Verb = triple_perF[2]
                    if Noun != Noun:
                        continue
                    print Report_id, SV_id[0], SV_id[1]
                    Result = self.Dc.predict(Noun, Particle, Verb)
                    DeepCase_unique = self.Dc.identify(Result)
                    # print Noun, Particle, Verb, DeepCase_unique

                    DeepCase_Noun_perV[self.Dc.DeepCaseList.index(DeepCase_unique)].append(Noun)

                    if index_perF == len(tripleFrame_Treport_sort[(tripleFrame_Treport_sort[u"文_id"] == SV_id[0]) & (
                        tripleFrame_Treport_sort[u"動詞_id"] == SV_id[1])]) - 1:
                        while [] in DeepCase_Noun_perV:
                            DeepCase_Noun_perV[DeepCase_Noun_perV.index([])] = [u" "]

                        for DeepCase_Noun_tmp in list(
                                itertools.product(DeepCase_Noun_perV[0], DeepCase_Noun_perV[1], DeepCase_Noun_perV[2],
                                                  DeepCase_Noun_perV[3], DeepCase_Noun_perV[4], DeepCase_Noun_perV[5],
                                                  DeepCase_Noun_perV[6])):
                            Verb_target.append(Verb)
                            Verb_target_id.append((Report_id, SV_id[0], SV_id[1]))
                            for Di in range(len(self.Dc.DeepCaseList)):
                                DeepCase_Noun[Di].append(DeepCase_Noun_tmp[Di])

                            DeepCase_Noun_perV = [[] for i in range(len(self.Dc.DeepCaseList))]

        cf_list = [
            (u"報告書_id", [i[0] for i in Verb_target_id]), (u"文_id", [i[1] for i in Verb_target_id]),
            (u"動詞_id", [i[2] for i in Verb_target_id]), (u"動詞", Verb_target)
        ]
        cf_list.extend([(self.Dc.DeepCaseList[i], DeepCase_Noun[i]) for i in range(len(self.Dc.DeepCaseList))])
        # cf_list.extend([(Dc.dummylist[2].columns[i], SurfaceCase_Noun[i]) for i in range(len(Dc.dummylist[2].columns))])

        case_frame = dict(cf_list)

        cd_columns = [u"報告書_id", u"文_id", u"動詞_id", u"動詞"]
        cd_columns.extend([self.Dc.DeepCaseList[i] for i in range(len(self.Dc.DeepCaseList))])
        # cd_columns.extend([Dc.dummylist[2].columns[i] for i in range(len(Dc.dummylist[2].columns))])

        case_df = DataFrame(case_frame, columns=cd_columns)
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
        Noun_weight = 2.0
        idf_Treport = Series(idf_Treport)
        zero = min(idf_Treport)
        if zero==0:
            min_idf=1.0
            for idf in idf_Treport:
                if idf<min_idf and idf!=zero:
                    min_idf=idf
            idf_Treport[idf_Treport == 0] = min_idf*0.5


        for frame in case_df[u"事象"].drop_duplicates().values:
            MorList_tmp = {}
            for i, words in enumerate(frame.split(u" ")):
                #print words, u":"
                if i==len(frame.split(u" "))-1:
                    if words[-2:] != u"する":
                        MorList_tmp[words] = idf_Treport[terms.index(words)]
                    else:
                        MorList_tmp[words[:-2]] = idf_Treport[terms.index(words[:-2])]
                    #エラー回避用xm
                    Noun_comp = u""
                else:
                    Lan = Language(words)
                    outList = Lan.getMorpheme()
                    Mor_1 = [outList[i][1] for i in range(len(outList))]
                    for mi, Mor in enumerate(outList):
                        if Mor_1[mi] == u"名詞" and Mor[2] != u"形容動詞語幹":
                            Noun_comp += Mor[0]
                            if mi < len(Mor_1) - 1:
                                if Mor_1[mi + 1] != u"名詞":
                                    #print Noun_comp,
                                    if Noun_comp in terms:
                                        MorList_tmp[Noun_comp] = idf_Treport[terms.index(Noun_comp)] * Noun_weight
                                    else:
                                        print "スキップされました。"

                                    Noun_comp = u""

                            else:
                                #print Noun_comp
                                if Noun_comp in terms:
                                    MorList_tmp[Noun_comp] = idf_Treport[terms.index(Noun_comp)] * Noun_weight
                                else:
                                    print "スキップされました。"
                                Noun_comp = u""
                        elif Mor_1[mi] != u"助詞" and Mor_1[mi] != u"助動詞" and Mor[5] != u"サ変・スル" and Mor[2] != u"接尾":
                            #print Mor[0]
                            tmp= Mor[0]
                            if tmp in terms:
                                MorList_tmp[Mor[0]] = idf_Treport[terms.index(Mor[0])]
                            else:
                                print "スキップされました"



            MorList.append(MorList_tmp)

        #caseFrame = case_df[u"主体"] + u" " + case_df[u"起点"] + u" " + case_df[u"対象"] + u" " + case_df[u"状況"] + u" " + case_df[
         #   u"着点"] + u" " + case_df[u"手段"] + u" " + case_df[u"関係"] + u" " + case_df[u"動詞"]
        cf = [i for i in case_df[u"事象"].drop_duplicates()]

        #Jaccard係数による統一辞書の作成
        Wdist_index = []
        Wdist_column = []
        Wdist = []
        unifyList = {}
        Case_freq = Counter(case_df[u"事象"])
        # 各文の動詞が反対語リストに含まれていれば分類しない
        oppositeList = [u"良好", u"正常", u"低下"]

        #距離計算は時間がかかる（24時間ぐらいかかる）ため、スキップ。（出力が出現の有無の行列だけでよいため）by上田
        print len(cf), len(MorList)
        for i, x in enumerate(MorList):
            print u"calculating distance... ", i
            x_keys_set = set(x.keys())
            for j, y in enumerate(MorList[i + 1:]):
                j = i + j + 1
                y_keys_set = set(y.keys())
                # print j
                if bool(x_keys_set.intersection(y_keys_set)) and cf[i] == cf[j]:
                    continue
                if bool(set(oppositeList).intersection(x_keys_set)) and not(bool(y_keys_set.issuperset(set(oppositeList).intersection(x_keys_set)))):
                    continue
                elif bool(set(oppositeList).intersection(y_keys_set)) and not(bool(x_keys_set.issuperset(set(oppositeList).intersection(y_keys_set)))):
                    continue

                if (x.keys() in unifyList.keys()) | (y.keys() in unifyList.keys()):
                    continue
                if bool(x_keys_set.intersection(y_keys_set)) and cf[i] != cf[j]:
                    sym = x_keys_set.symmetric_difference(y_keys_set)
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
                    xy_set = dict(x.items() + y.items())
                    xy_insec = x_keys_set.intersection(y_keys_set)
                    w_all = 0.00
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
                    for mor_val in xy_insec:
                        w_insec += xy_set[mor_val]
                    dist_str = w_insec / w_all
                    if dist_str >= threshould_dist:
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

        Wdist = DataFrame(Wdist, index=[Wdist_index, Wdist_column], columns=[u"Similarity"])

        fnc = lambda x: unifyList.get(x, x)
        insecset = set()
        while set(case_df[u"事象"]).intersection(set(unifyList.keys())):
            if insecset== set(case_df[u"事象"]).intersection(set(unifyList.keys())):
                break
            case_df[u"事象"] = case_df[u"事象"].map(fnc)
            insecset = set(case_df[u"事象"]).intersection(set(unifyList.keys()))
        return case_df, Wdist
    #ゼロ代名詞が含まれると判断するニューラルネットワークの出力の閾値の算出
    def Cal_thresold(self, case_df, output_thresold):
        NNoutputList = []
        for Report_id in case_df[u"報告書_id"].drop_duplicates():
            print u"Calculating thresold:", Report_id
            case_df_perR = case_df[case_df[u"報告書_id"] == Report_id]
            for first_Sen, Sentence_id in enumerate(case_df_perR[u"文_id"].drop_duplicates()):
                for line in case_df_perR[case_df[u"文_id"] == Sentence_id].iterrows():
                    for di, l in enumerate(line[1][4:11].values):
                        if l != u" ":
                            NNoutputList.append([i[1] for i in self.Dc.predict(l, u"", line[1][3])])
        maxList_perD = [[] for i in xrange(0, 7)]
        thresold_perD = [[] for i in xrange(0, 7)]
        for perline in NNoutputList:
            for out_perline in perline:
                maxList_perD[out_perline.index(max(out_perline))].append(max(out_perline))

        while [] in maxList_perD:
            maxList_perD[maxList_perD.index([])] = [0.0]

        for i, mlp in enumerate(maxList_perD):
            thresold_perD[i] = np.percentile(np.array(mlp), output_thresold)
            print i
            print Series(mlp).describe()
        return maxList_perD, thresold_perD
    #因果連鎖分割（因果連鎖番号の割り当て）
    def Section_div(self, case_df, VC_Dc, thresold_perD):

        Record_id = dict()  # 文_id:レコード_id
        Record_id[(case_df.ix[0, :][u"報告書_id"], case_df.ix[0, :][u"文_id"])] = 0
        tail_key = -1
        for Report_id in case_df[u"報告書_id"].drop_duplicates():
            print u"Extracting Sec_id:", Report_id
            Noun_pre = dict()
            # print Report_id
            case_df_perR = case_df[case_df[u"報告書_id"] == Report_id]
            for first_Sen, Sentence_id in enumerate(case_df_perR[u"文_id"].drop_duplicates()):

                for line in case_df_perR[case_df[u"文_id"] == Sentence_id].iterrows():
                    # print line[1][1]
                    # print line[1][3]
                    if line[1][1] not in Noun_pre.keys():
                        Noun_pre[line[1][1]] = [l for l in line[1][4:11].values if l != u" "]
                    else:
                        Noun_pre[line[1][1]] = Noun_pre[line[1][1]] + [l for l in line[1][4:11].values if l != u" "]
                    # 代名詞の補完
                    for di, l in enumerate(line[1][4:11].values):
                        if l != u" ":
                            Lan = Language(l)
                            outList = Lan.getMorpheme()
                            if set([u"代名詞"]).intersection(set([outList[i][2] for i in range(len(outList))])):
                                # '''
                                #代名詞の出力ベクトルと名詞の出力ベクトルのユークリッド距離が最小の名詞を選択
                                pronoun_vec = [np.array(out_perD[1]) for out_perD in self.Dc.predict(l, u"", line[1][3]) if
                                               np.argmax(np.array(out_perD[1])) == di]
                                if len(pronoun_vec) == 0:
                                    pronoun_vec = [np.array(out_perD[1]) for out_perD in self.Dc.predict(l, u"", line[1][3])]
                                Noun_out = [
                                    {Np: [np.array(output[1]) for output in self.Dc.predict(Np, u"", line[1][3])] for Np in
                                     Np_list if Np not in line[1][4:11].values} for Np_list in
                                    [Noun_pre[line[1][1] - pre_i] for pre_i in range(0, 2) if
                                     line[1][1] - pre_i in Noun_pre.keys()]]

                                if len(Noun_out[0]) == 0:
                                    del Noun_out[0]
                                if len(Noun_out) == 0:
                                    break

                                Neuclid_perS = [
                                    {n: min([np.linalg.norm(pv - vec) for vec in No[n] for pv in pronoun_vec]) for n in
                                     No.keys()} for No in Noun_out]
                                Neuclid_min_perS = [(perS.keys()[perS.values().index(min(perS.values()))], min(perS.values())) for perS in Neuclid_perS]
                                toNoun = [N_ed[0] for N_ed in Neuclid_min_perS if
                                          min([nmp[1] for nmp in Neuclid_min_perS]) == N_ed[1]]
                                case_df.ix[line[0], u"事象"] = case_df.ix[line[0], u"事象"].replace(l, toNoun[0])
                                Noun_pre[line[1][1]][Noun_pre[line[1][1]].index(l)] = toNoun[0]
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
                    for i in [VC_Dc[VC] for VC in self.Dc.NV_class[1][line[1][3]] if VC in VC_Dc]:
                        Deep_cand += i
                    Count_perD = [Deep_cand.count(d) for d in self.Dc.DeepCaseList]
                    Dc_toV = [Deep_cor for Deep_cor in
                              [d for d, Deep_cor in zip(self.Dc.DeepCaseList, Count_perD) if
                               sum(Count_perD) / float(len(Count_perD)) < Deep_cor]]

                    Noun_zero = dict()
                    for Dc_tmp in Dc_toV:
                        if line[1][Dc_tmp] == u" ":
                            Noun_out = [{Np: max([output[1][self.Dc.DeepCaseList.index(Dc_tmp)] for output in self.Dc.predict(Np, u"", line[1][3])]) for Np in Np_list if Np not in line[1][4:11].values} for Np_list in [Noun_pre[line[1][1] - pre_i] for pre_i in range(0, 2) if
                                                    line[1][1] - pre_i in Noun_pre.keys()]]
                            while {} in Noun_out:
                                Noun_out.remove({})
                            if len(Noun_out) == 0:
                                continue
                            MaxN_perS = [No[No.keys()[No.values().index(max(No.values()))]] for No in
                                         Noun_out]
                            SSen_rec = MaxN_perS.index(max(MaxN_perS))
                            if max(MaxN_perS) > thresold_perD[self.Dc.DeepCaseList.index(Dc_tmp)]:
                                Noun_zero[Dc_tmp] = Noun_out[SSen_rec].keys()[Noun_out[SSen_rec].values().index(max(MaxN_perS))]
                    if len(Noun_zero.keys()) > 0:
                        case_zero = u""
                        for d, Noun_perD in zip(line[1][4:11].keys(), line[1][4:11].values):
                            if d in Noun_zero.keys():
                                case_zero += u" " + Noun_zero[d]
                            else:
                                case_zero += u" " + Noun_perD
                        case_zero += u" " + line[1][3]
                        case_zero = re.sub(r" +", u" ", case_zero.strip())

                        case_df.ix[line[0], u"事象"] = case_zero
                        for Noun_zero_tmp in Noun_zero.values():
                            Noun_pre[line[1][1]].append(Noun_zero_tmp)

                # 前の文に含まれる名詞が含まれているか
                if first_Sen == 0 and tail_key != -1:
                    Record_id[(Report_id, Sentence_id)] = Record_id[tail_key] + 1
                    continue
                for pre_i in range(3, 0, -1):
                    if line[1][1] - pre_i in Noun_pre.keys():
                        if set(Noun_pre[line[1][1]]).intersection(set(Noun_pre[line[1][1] - pre_i])):
                            for pre_j in range(pre_i, -1, -1):
                                if line[1][1] - pre_j in Noun_pre.keys():
                                    Record_id[(Report_id, Sentence_id - pre_j)] = Record_id[
                                        (Report_id, line[1][1] - pre_i)]
                            break
                        else:
                            Record_id[(Report_id, Sentence_id)] = Record_id[(Report_id, line[1][1] - pre_i)] + 1
                while (Report_id, Sentence_id) not in Record_id.keys():
                    pre_i += 1
                    if (Report_id, Sentence_id - pre_i) in Record_id.keys():
                        Record_id[(Report_id, Sentence_id)] = Record_id[(Report_id, line[1][1] - pre_i)] + 1
                if first_Sen == len(case_df_perR[u"文_id"].drop_duplicates()) - 1:
                    tail_key = (Report_id, Sentence_id)

        case_df[u"レコード_id"] = [(i, j) for i, j in zip(case_df[u"報告書_id"], case_df[u"文_id"])]
        case_df[u"レコード_id"] = case_df[u"レコード_id"].map(lambda x: Record_id[x])
        return case_df


