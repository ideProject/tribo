dict = {}
for i,sinsou in enumerate(a):
    dict[sinsou]=clusterN[i]

for i in dict.keys():
    print i,dict[i]


grouped = frame4.groupby(dict, axis =0)


for index in grouped.sum().index:
    cluhyou = grouped.sum().ix[index,:].order(ascending=False)
    print index
    print cluhyou,"\n"