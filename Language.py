# coding: utf-8
import subprocess
from subprocess import Popen, PIPE
import shlex
import xml.etree.ElementTree as ET


class Language:
    """自然言語処理"""

    def __init__(self, str):
        self.str = str

    #mecabの処理をして返してくれる
    def getMorpheme(self):
        # out = subprocess.check_output("echo %s | mecab" %self.str,shell=True)
        out = subprocess.check_output("echo %s | mecab" % self.str.encode("shift-jis"), shell=True) #mecabに名詞を投げて、レスポンスをoutに入れている
        meout = []
        for line in out.split("\n"):    #mecabの解析結果を行ごとにsplitしている
            if line == "EOS\r":
                break
            line_new = line.replace("\t", ",")
            meout.append(line_new.decode('shift-jis'))
        outlist = []
        for record in meout:
            outlist.append(record.split(u","))
        return outlist  #mecabの解析結果すべてを','で分けたもの(リスト型)を返している

    def cabocha_command(self, cmd_option="-f3"):
        out = subprocess.check_output("echo %s | cabocha %s" % (self.str.encode("shift-jis"), cmd_option), shell=True)
        return out.decode("shift-jis")

    def chunk_structured(self, cabocha_xml):
        elem = ET.fromstring(cabocha_xml.encode("utf-8"))  # ElementTree--XMLデータを解析するパッケージ
        chunkinfo = []
        tokinfo = []
        sentence_tok = []
        for chunklist in elem.findall(u".//chunk"):
            chunkinfo.append(dict(chunklist.items()))  # head,rel,score,link,func,idの情報を辞書型でappendしている
            tokinfo_tmp = []
            sentence_tok_tmp = []
            for toklist in chunklist.findall(u".//tok"):        #toklist--[('id',''),('feature',)]って感じ

                # print "aaaaaaaaaaa"
                # print chunklist.items()
                # print "bbbbbbbbbbb"
                # print toklist.items()

                tokinfo_tmp.append(tuple(toklist.items()[1][1].split(u",")))        #toklist--cabochaで解析した出力が入っている　名詞、接続*,*,*,*,使用、シヨウ、ショー、的な
                sentence_tok_tmp.append(toklist.text)
            #for文終わりでchunklist内の情報がtoklistを通じてtokinfo_tmpに書き込まれている
            tokinfo.append(tuple(tokinfo_tmp))
            sentence_tok.append(tuple(sentence_tok_tmp))
        return chunkinfo, tokinfo, sentence_tok
