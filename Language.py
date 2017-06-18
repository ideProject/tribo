# coding: utf-8
import subprocess
from subprocess import Popen, PIPE
import shlex
import xml.etree.ElementTree as ET

class Language:
    """自然言語処理"""
    def __init__(self, str):
        self.str=str
        
    def getMorpheme(self):
        #out = subprocess.check_output("echo %s | mecab" %self.str,shell=True)
        out = subprocess.check_output("echo %s | mecab" %self.str.encode("shift-jis"),shell=True)
        meout=[]
        for line in out.split("\n"):
            if line == "EOS\r":
                break
            line_new = line.replace("\t", ",")
            meout.append(line_new.decode('shift-jis'))
        
        outlist=[]
        for record in meout:
            outlist.append(record.split(u","))
        
        return outlist

    def cabocha_command(self, cmd_option="-f3"):       
       out = subprocess.check_output("echo %s | cabocha %s" %(self.str.encode("shift-jis"), cmd_option), shell=True)
       return out.decode("shift-jis")
    
    def chunk_structured(self, cabocha_xml):
        elem = ET.fromstring(cabocha_xml.encode("utf-8"))
        chunkinfo=[]
        tokinfo=[]
        sentence_tok=[]
        for chunklist in elem.findall(u".//chunk"):
            chunkinfo.append(dict(chunklist.items()))
            tokinfo_tmp=[]
            sentence_tok_tmp=[]        
            for toklist in chunklist.findall(u".//tok"):
                tokinfo_tmp.append(tuple(toklist.items()[1][1].split(u",")))
                sentence_tok_tmp.append(toklist.text)
            tokinfo.append(tuple(tokinfo_tmp))
            sentence_tok.append(tuple(sentence_tok_tmp))
        return chunkinfo, tokinfo, sentence_tok
