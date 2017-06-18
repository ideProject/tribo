# -*- coding: utf-8 -*-
sindict={
        '人？':'人',
        '動作主？':'動作主',
        '動作主（操作対象）':'動作主',
        'actor?':'動作主',
        'causer':'動作主',
        '動作？':'動作',
        '場所・容器':'場所',
        '場所・起点':'場所',
        '場所（方向・着点）':'場所',
        '変化先？': '変化先',
        '対象（人）':'対象',
        '対象(人)':'対象',
        '対象（生物）':'対象',
        '対象（身体部分）':'対象',
        '対象？':'対象',
        '方向（人）':'方向',
        '方向？':'方向',
        '着点（人）':'着点',
        '着点（身体部分）':'着点',
        '着点？':'着点',
        '経路？':'経路',
        '経験者（偶然）':'経験者',
        '経験者（操作対象）':'経験者',
        '経験者（達成）':'経験者',
        '経験者？':'経験者',
        '起点（人）':'起点',
        '内容物？':'内容物',
        
        '期限':'時',
        '期間':'時',
        '決定内容':'対象',
        '補文':'対象',
        '事態':'対象',
        '感情':'対象',
        '交換対象':'相互',
        '相手':'相互',
        '関係':'相互',
        '媒介':'対象',
        '数量':'着点',
        '結果物':'補語相当',
        

        }


hyoudict={
        "で・に": "に・で",
        "と・に": "に・と",
        "に・と?に": "に・と",
        "は・に": "に・は",
        
        }
        
        
   
'''     
fs = lambda x: sindict.get(x,x)
frame3.index = frame3.index.map(fs)
fh = lambda x: hyoudict.get(x,x)
frame3.columns = frame3.columns.get_level_values(1).map(fh)

frame3_1=frame3
frame3_1.index.names=['深層格']
f_grouped=frame3_1.groupby(frame3_1.index)
frame3_2=f_grouped.sum()
frame3_2.columns.names=['表層格']
f_grouped=frame3_2.groupby(frame3_2.columns, axis=1)
frame4=f_grouped.sum()

'''


'''
droplist=[]
for i in range(len(frame4)):
   if frame4.sum(axis=1)[i]<2:            
       print frame4.index[i]
       droplist.append(frame4.index[i])
droplist.append('起点・着点')
droplist.append('その他')
frame4_1 = frame4.drop(droplist,axis=0)
'''
#frame5=frame4_1.div(frame4_1.sum(1),axis=0)
        
