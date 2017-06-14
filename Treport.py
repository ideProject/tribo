# -*- coding: utf-8 -*-
import sys
sys.path.append("C:\Users\ide\Dropbox\python")

from Language import Language
import xlrd
import pickle
from Word_class import Word_class
import re
import unicodedata
from pandas import Series

class Treport:
    def __init__(self, path):
        book = xlrd.open_workbook(path)
        sheets = book.sheets()
        self.s = sheets[0]
    
    def NV_class_load(self, NV_classpath):
        file = open(NV_classpath.decode("shift-jis").encode("utf-8"))
        NV_class = pickle.load(file)
        return NV_class
    

                
    def uniqword(seq):
        seen = set()
        seen_add = seen.add
        return [ x for x in seq if x not in seen and not seen_add(x)]    
    
    def delete_unnecc(self, i):
        noenc = self.s.cell_value(i,3).replace(u'－',u'-')
        noenc = noenc.replace(u'～',u'~')
        noenc = noenc.replace(u'',u'')#不要報告書
        noenc = noenc.replace(u'Ⅰ',u'1')
        noenc = noenc.replace(u'Ⅱ',u'2')
        noenc = noenc.replace(u'Ⅲ',u'3')
        noenc = noenc.replace(u'Ⅳ',u'4')
        noenc = noenc.replace(u'Ⅴ',u'5')
        noenc = noenc.replace(u'ⅰ',u'1')
        noenc = noenc.replace(u'ⅱ',u'2')
        noenc = noenc.replace(u'ⅲ',u'3')
        noenc = noenc.replace(u'ⅳ',u'4')
        noenc = noenc.replace(u'ⅴ',u'5')
        noenc = noenc.replace(u'⑪',u'11')
        noenc = noenc.replace(u'⑫',u'12')
        noenc = noenc.replace(u'⑰',u'17')
        noenc = noenc.replace(u'⑲',u'19')
        noenc = noenc.replace(u'№',u'No.')
        noenc = noenc.replace(u'㎎',u'mg')    
        noenc = noenc.replace(u'㎜',u'mm')
        noenc = noenc.replace(u'㎡',u'm^2')
        noenc = noenc.replace(u'㍑',u'リットル')
        noenc = noenc.replace(u'槢',u'摺')
        noenc = noenc.replace(u'<',u'＜')
        noenc = noenc.replace(u'>',u'＞')
        return noenc
                
    def NV_extract(self):
        NList=[]
        VList=[]
        for i in range(1, self.s.nrows):
            print i            
            noenc = self.delete_unnecc(i)
            lan = Language(noenc)
            if len(lan.str)>4000:
                continue
            word = lan.getMorpheme()
            tmpNoun =u""
            NN=0
            for j, line in enumerate(lan.getMorpheme()):
                if line[1]==u"動詞":
                    if line[7]==u"する":
                        VList.append(word[j-1][0]+line[7])
                    else:
                        VList.append(line[7])
            
                if line[1]==u"名詞" and j!=len(word)-1:
                    if word[j+1][1]==u"名詞":
                        tmpNoun+=line[0]
                        NN+=1
                        if NN >3:
                            tmpNoun=u""
                            NN=0
                            continue
                    elif word[j+1][7]!=u"する":
                        NList.append(tmpNoun+line[0])
                        tmpNoun=u""
                        NN=0
        return NList, VList
        
    if __name__ =='__main__':
        path = u'D:/研究/データ/report_data_ver4_1.xlsx'
        from Treport import Treport
        TR = Treport(path)
        NV_classpath="C:/tmp/Evaluation/NV_class.Word"
        NV_class = TR.NV_class_load(NV_classpath)
        NList, VList = TR.NV_extract()    
        
        Wc = Word_class(NV_class)
        fnc = lambda x: Wc.Nclass.get(x,"No entry")
        Noun_uniq = uniqword(NList)
        Noun_uniq2 = Series(Noun_uniq).map(fnc)
        
        fvc = lambda x: Wc.Vclass.get(x,"No entry")
        Verb_uniq = uniqword(VList)
        Verb_uniq2 = Series(Verb_uniq).map(fvc)
    
        Noun_uniq3=[]
        for N in list(Series(Noun_uniq)[Noun_uniq2=="No entry"]):
            numin = False
            alpha = False
            N_uni = unicodedata.normalize('NFKC', N)
            if re.search("[0-9]", N_uni):
                numin = True
            if re.search("[{-~]", N_uni) or re.search("[[-`]", N_uni) or re.search("[ -/]", N_uni) or re.search("[:-@]", N_uni):
                alpha = True
            
            if numin is False and alpha is False:
                Noun_uniq3.append(N_uni)
        
        Verb_uniq3=[]
        for V in list(Series(Verb_uniq)[Verb_uniq2=="No entry"]):
            numin = False
            alpha = False
            V_uni = unicodedata.normalize('NFKC', V)
            if re.search("[0-9]", V_uni):
                numin = True
            if re.search("[{-~]", V_uni) or re.search("[[-`]", V_uni) or re.search("[ -/]", V_uni) or re.search("[:-@]", V_uni):
                alpha = True
            
            if numin is False and alpha is False:
                Verb_uniq3.append(V_uni)
        
        Noun_tail=[]
        i=0
        for compN in Noun_uniq3:
            print i
            i+=1
            lan = Language(compN)
            word = lan.getMorpheme()
            Noun_tail.append(word[len(word)-1][0])
        
        Noun_tail_uniq = uniqword(Noun_tail)
        Noun_tail_uniq2 = Series(Noun_tail_uniq).map(fnc)
        
        Noun_tail_uniq3=[]
        for N in list(Series(Noun_tail_uniq)[Noun_tail_uniq2=="No entry"]):
            Noun_tail_uniq3.append(N)
