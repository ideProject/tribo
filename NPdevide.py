# -*- coding: utf-8 -*-
import Language
class NPdevide:        
    def chasen(self,data):
        NPlist=[]
        for i,str in enumerate(data[u"体言助詞".encode('utf-8')]):
        #for i,str in enumerate(data.ix[:,2]):
            print i
            lan=Language(str)
            NPlist.extend(lan.getMorpheme())
        return NPlist
    
    def hinshi(self,NPlist):
        NList=[]
        PList=[]
        OtherList=[]
        tmpword = NPlist[0].split(",")[0]
        wflag = True
        for i,line in enumerate(NPlist):
            new_line = line.split(",")
            if i == len(NPlist)-1:
                break
            
            next_line = NPlist[i+1].split(",")
                
            if wflag == True:
                tmpword = new_line[0]
                
            if new_line[1]!=next_line[1]:
                if new_line[1].decode('shift-jis')==u"名詞" and next_line[1].decode('shift-jis')==u"助詞":
                    NList.append(tmpword)
                    PList.append(next_line[0])
                else:
                    OtherList.append(tmpword)
                wflag = True
            else:
                tmpword += next_line[0]
                wflag = False
        return NList, PList, OtherList
        
    def a(self, data, NList, PList, NP):
        for i, str in enumerate(NP):
            indexList = data[u"体言助詞".encode("utf-8")][data[u"体言助詞".encode("utf-8")]==str.decode('shift-jis').encode('utf-8')].index.tolist()
            for ii in indexList:
                data.ix[ii, "体言"] = NList[i].decode('shift-jis')
                data.ix[ii, "助詞"] = PList[i].decode('shift-jis')
        return data                

        
                
    '''
    with open("C:/tmp/mecab_output.csv","w") as fpw:
        for line in NPlist:
            fpw.write(line)
    '''                