# -*- coding: utf-8 -*-
neu_input = pd.concat([dummylist[0],dummylist[1],dummylist[2]],axis=1)
input_mean = neu_input.mean(0)

SenAna_result = [[],[],[],[],[],[],[]]
for il in input_mean.index:
    resultlist=[[],[],[],[],[],[],[]]
    for input_target in [0.1*ran for ran in range(11)]:
        X=[]
        for i in input_mean.index:
            if il==i:
                X.append(input_target)
            else:
                X.append(input_mean[i])
        result = net.activate(X).tolist()
        for oi, output in enumerate(result):
            resultlist[oi].append(output)
    for oi_perD, output_perD in enumerate(resultlist):
        if output_perD.index(min(output_perD))<output_perD.index(max(output_perD)):
            SenAna_result[oi_perD].append(max(output_perD)-min(output_perD))
        else:
            SenAna_result[oi_perD].append(min(output_perD)-max(output_perD))                  
SenAna_frame = DataFrame(SenAna_result,index=Ddummy.columns,columns=input_mean.index).T

for Deepcase in Ddummy.columns:
    Deepcase = u"主体"
    num =15
    SenAna_frame.sort(Deepcase,ascending=False)[Deepcase].head(num).plot(kind='bar')
    plt.title(Deepcase)
    plt.xlabel("input")
    plt.ylabel("Difference value of max and min")
