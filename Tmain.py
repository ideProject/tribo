# -*- coding: utf-8 -*-

from Cases_extract import Cases_extract
from pandas import DataFrame
from pandas import Series
import pandas as pd
import itertools
import pickle
import math
from Deepcase import Deepcase
import re
import random

path_List={
    #学習済みニューラルネットワーク
    "Neural_network": "data/Trained.Network",
    #ニューラルネットワークの入出力
    "dummylist": "data/dummylist.Word",
    #名詞・動詞クラスの辞書
    "NV_class": "data/NV_class.Word",
    #診断報告書
    "Treport": 'data/report_data_ver4_2_moribden.xlsx',
    #抽出したトリプル「名詞＋助詞＋動詞」
    "Triple": "data/Triple.csv",
    #事象を表すトリプルリスト
    "Triple_Treport": "data/Triple_Treport.csv",
    #名詞クラスに登録されていない名詞
    "Un_Nounclass": "data/unregistered_NounsClass.csv",
    #動詞クラスに登録されていない語句
    "Un_Verbclass": "data/unregistered_Verbs(bunruidb)Class.csv",
    #分類語彙表（シソーラス）
    "bunruidb": "data/bunruidb.txt",
    #分類語彙表と動詞項構造シソーラスの共起頻度（動詞）
    "Tobun_FromVthe": "data/bunruidb_Vthesaurus.csv",
    #抽出した格フレーム
    "caseframe": "data/caseframe.csv",
    #抽出した単語リスト
    "terms_list": 'data/terms.list',
    #抽出した文書ごとの単語リスト
    "documents_list": 'data/documents.list',
    #単語ごとのidf
    "idf_Treport_list": 'data/idf_Treport.list',
    #診断報告書における診断対象の機械の分類結果（設備クラスタ）
    "Tcluster": ("data/Tcluster.xls","Sheet1"),
    #学部研究で分類した設備クラスタに含まれるデータにおける格フレーム
    "caseframe_Tcluster": "data/caseframe_Tcluster.csv",
    #分類語彙表と動詞項構造シソーラスの共起頻度
    "VC_Dc": 'data/VC_Dc.list',
    #格フレームに因果連鎖番号を割り当てた結果
    "caseframe_sec": "data/caseframe_Tcluster_sec.csv",
    #類似度の高い文の組
    "Wdist": "data/Wdist.csv",
    #設備クラスタ毎の格フレーム（%s -> number）
    "caseframe_number": "data/case_frame_%s.csv",
    "caseframe_ClusterNumber": "data/case_frame_クラスター-%s.csv",
    #報告書ごとの事象の頻度行列
    "case_mat": "data/case_mat_moribden%s.csv",
    "case_mat2": "data/case_mat2_moribden%s.csv"
}

def tf(terms, document):
    # TF値の計算。単語リストと文章を渡す
    tf_values = [document.count(term) for term in terms]
    return list(map(lambda x: x / sum(tf_values), tf_values))


def idf(terms, documents):
    # IDF値の計算。単語リストと全文章を渡す
    return [math.log10(len(documents) / sum([bool(term in document) for document in documents])) for term in terms]


def tf_idf(terms, documents):
    # TF-IDF値を計算。文章毎にTF-IDF値を計算
    return [[_tf * _idf for _tf, _idf in zip(tf(terms, document), idf(terms, documents))] for document in documents]

if __name__ == "__main__":
    # 全トリプルの抽出
    Dc = Deepcase(path_List["Neural_network"], path_List["dummylist"], path_List["NV_class"])
    Ce= Cases_extract(Dc)

    triplelist = Ce.Triple_extract(path_List["Treport"])
    Nounlist = []
    Particlelist = []
    Verblist = []
    Ridlist = []
    Sidlist = []
    Vidlist = []
    for T_keys, T_values in zip(triplelist.keys(), triplelist.values()):
        for tri_tmp in T_values:
            Nounlist.append(tri_tmp[0])
            Particlelist.append(tri_tmp[1])
            Verblist.append(tri_tmp[2])
            Ridlist.append(T_keys[0])
            Sidlist.append(T_keys[1])
            Vidlist.append(T_keys[2])
    tripleFrame = DataFrame({u"報告書_id":Ridlist, u"文_id":Sidlist, u"動詞_id":Vidlist, u"名詞":Nounlist, u"助詞":Particlelist, u"動詞":Verblist}, columns=[u"報告書_id", u"文_id", u"動詞_id", u"名詞", u"助詞", u"動詞"])
    tripleFrame.sort_index(by=[u"報告書_id", u"文_id", u"動詞_id"], inplace=True)
    tripleFrame[u"報告書_id"] = [int(i) for i in tripleFrame[u"報告書_id"]]
    tripleFrame.to_csv(path_List["Triple"], index=False, encoding='shift-jis')
    #'''
    # トリプルから事象の抽出
    #'''
    # tripleFrame = pd.read_csv(path_List["Triple"], encoding='shift-jis')
    # tripleFrame_Treport = Ce.TNoun_extract(tripleFrame, Dc.NV_class)
    # tripleFrame_Treport.sort_index(by=[u"報告書_id", u"文_id", u"動詞_id"], inplace=True)
    # tripleFrame_Treport.to_csv(path_List["Triple_Treport"], index=False, encoding='shift-jis')
    #'''
    # 未登録語の登録
    '''
    Dc.unregistered_words(path_List["Un_Nounclass"], path_List["Un_Verbclass"])
    Dc.buruidb_verbs(path_List["bunruidb"], path_List["Tobun_FromVthe"])
    '''
    #'''
    #格フレームの構築
    tripleFrame_Treport = pd.read_csv(path_List["Triple_Treport"], encoding='shift-jis')
    case_df = Ce.create_caseframe(tripleFrame_Treport)
    case_df.to_csv(path_List["caseframe"], encoding='shift-jis', index=False)
    #'''
    case_df = pd.read_csv(path_List["caseframe"], encoding='shift-jis')
    #語句の重み（idf）算出
    '''
    terms, documents = Ce.extract_terms(case_df)
    idf_Treport = idf(terms, documents)

    file = open(path_List["terms_list"], 'w')
    pickle.dump(terms, file)
    file.close()
    file = open(path_List["documents_list"], 'w')
    pickle.dump(documents, file)
    file.close()
    file = open(path_List["idf_Treport_list"], 'w')
    pickle.dump(idf_Treport, file)
    file.close()
    '''

    file = open(path_List["terms_list"])
    terms = pickle.load(file)
    file.close()
    file = open(path_List["documents_list"])
    documents = pickle.load(file)
    file.close()
    file = open(path_List["idf_Treport_list"])
    idf_Treport = pickle.load(file)
    file.close()

    #設備クラスタ（学部研究で分類した似た特徴を持つ設備）が含まれる報告書の抽出
    print "Tclusterを開いています..."
    EXL = pd.ExcelFile(path_List["Tcluster"][0])  # xlsxファイルをPython上で開く
    print"読み込み完了"
    Tcluster = EXL.parse(path_List["Tcluster"][1])

    #case_df_Tcluster = case_df.ix[case_df[u"報告書_id"].map(lambda x: x in list(Tcluster[u"分析NO"].drop_duplicates())), :]
    #case_df_Tcluster.to_csv(path_List["caseframe_Tcluster"], encoding='shift-jis', index=False)

    case_df_Tcluster = pd.read_csv(path_List["caseframe_Tcluster"], encoding='shift-jis')
    '''
    #動詞項構造シソーラスと対応する分類語彙表の動詞クラスの抽出
    VC_list = case_df_Tcluster[u"動詞"].map(lambda x: Dc.NV_class[1].get(x, ""))
    Fre_VC_Dc = dict()
    for i, VC_perV in zip(VC_list.keys(), VC_list.values):
        Dc_count_tmp = [int(x) for x in case_df_Tcluster.ix[i, Dc.DeepCaseList] != u" "]
        for VC in VC_perV:
            if VC in Fre_VC_Dc.keys():
                Fre_VC_Dc[VC] = [x + y for x, y in zip(Fre_VC_Dc[VC], Dc_count_tmp)]
            else:
                Fre_VC_Dc[VC] = Dc_count_tmp
    times = 2.0
    VC_Dc = dict()
    for i in Fre_VC_Dc.keys():
        TW = sum(Fre_VC_Dc[i]) * (1 / float(len(Fre_VC_Dc[i]))) * times
        Dc_perVc = [Dc.DeepCaseList[Fre_VC_Dc[i].index(x)] for x in Fre_VC_Dc[i] if x > TW]
        VC_Dc[i] = Dc_perVc
    file = open(path_List["VC_Dc"], 'w')
    pickle.dump(VC_Dc, file)
    file.close()
    '''
    #省略語の補完と因果連鎖分割
    #'''
    # file = open(path_List["VC_Dc"])
    # VC_Dc = pickle.load(file)
    # file.close()
    # output_thresold = 80
    # maxList_perD, thresold_perD = Ce.Cal_thresold(case_df_Tcluster, output_thresold)
    # case_df_Tcluster_sec = Ce.Section_div(case_df_Tcluster, VC_Dc, thresold_perD)
    # case_df_Tcluster_sec.to_csv(path_List["caseframe_sec"], encoding='shift-jis', index=False)
    #'''

    #事象間の類似度算出
    case_df_Tcluster_sec = pd.read_csv(path_List["caseframe_sec"], encoding='shift-jis')
    cases = case_df_Tcluster_sec[u"主体"] + " " + case_df_Tcluster_sec[u"起点"] + " " + case_df_Tcluster_sec[u"対象"] + " " + case_df_Tcluster_sec[u"状況"] + " " + \
            case_df_Tcluster_sec[u"着点"] + " " + case_df_Tcluster_sec[u"手段"] + " " + case_df_Tcluster_sec[u"関係"] + " " + case_df_Tcluster_sec[u"動詞"]
    for i in range(0, len(cases)):
        cases[i] = re.sub(r" +", u" ", cases[i].strip())
    pro_zeroNoun = case_df_Tcluster_sec.ix[case_df_Tcluster_sec[u"事象"] != cases, :]
    #類似度算出手法及び、統合する類似度の閾値
    dist_method = u"Jaccard"
    threshould_dist = 0.4
    #dist_method = u"Simpson"
    #threshould_dist = 0.5

    #'''
    # 確認データ数
    N = 1000
    ExNlist = random.sample(case_df_Tcluster_sec[u"報告書_id"].drop_duplicates(), N)
    case_df_Tcluster_sec = case_df_Tcluster_sec.ix[case_df_Tcluster_sec[u"報告書_id"].map(lambda x: x in ExNlist), :]
    #'''

    case_df_unified, Wdist = Ce.bunrui_frame(case_df_Tcluster_sec, terms, idf_Treport, dist_method, threshould_dist)
    Wdist.sort_values(by=u"Similarity", ascending=False).to_csv(path_List["Wdist"], encoding='shift-jis')

    Wdist = pd.read_csv(path_List["Wdist"], encoding='shift-jis')

    #設備クラスタごとに事象の出現の有無(0, 1)行列の作成
    for cluster in Tcluster[u"$T1-TwoStep"].drop_duplicates():
        if cluster != u"-1":
            id_perC_tmp = set(Tcluster[Tcluster[u"$T1-TwoStep"] == cluster][u"分析NO"]).intersection(
                set(case_df_unified[u"報告書_id"]))
            if len(id_perC_tmp) != 0:
                print cluster
                path = path_List["caseframe_number"] % cluster
                case_df_unified.ix[case_df_unified[u"報告書_id"].map(lambda x: x in id_perC_tmp), :].to_csv(path, encoding="shift-jis", index=False)

    case_df_perTc=[[] for i in range(0,4)]
    case_mat = [[] for i in range(0, 4)]
    Fre1_cases = [[] for i in range(0, 4)]
    case_mat2 = [[] for i in range(0, 4)]

    for Ci in range(0,4):
        ClusterN= Ci+1
        path = path_List["caseframe_ClusterNumber"] % ClusterN
        case_df_perTc[Ci] = pd.read_csv(path, encoding='shift-jis')

        case_mat[Ci] = pd.pivot_table(case_df_perTc[Ci].loc[:, [u"レコード_id", u"事象"]], index=u"レコード_id", columns=u"事象",
                              aggfunc=len).fillna(0)
        case_mat[Ci][case_mat[Ci] > 1] = 1
        cm_path = path_List["case_mat"] % ClusterN
        case_mat[Ci].to_csv(cm_path, encoding='shift-jis', index=False)
        #出現頻度1の事象を抽出
        Fre1_cases[Ci] = case_mat[Ci].columns[case_mat[Ci].sum() == 1]
        Fc_path = u"data/Fre1_cases_%s.csv" % ClusterN
        Series(Fre1_cases[Ci]).to_csv(Fc_path, encoding='shift-jis', index=False)
        #出現頻度1以上の事象を抽出
        indexer = case_mat[Ci].sum() > 1
        case_mat2[Ci] = case_mat[Ci][indexer.index[indexer]]
        columner = case_mat2[Ci].sum(1) > 0
        case_mat2[Ci] = case_mat2[Ci].ix[columner, :]
        cm2_path = path_List["case_mat2"] % ClusterN
        case_mat2[Ci].to_csv(cm2_path, encoding='shift-jis', index=False)

