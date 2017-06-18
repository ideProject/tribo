# -*- coding: utf-8 -*-
from pandas import DataFrame
import pandas as pd
import numpy as np

def Co_occurrence(frame_from, field1, field2):
    field_set = field1+u'_'+field2
    frame_to = DataFrame({field1:frame_from[field1], field2:frame_from[field2]})
    frame_to[field_set]= frame_to[field1]+u'_'+frame_to[field2]
    casecounts = frame_to[field_set].value_counts()
    frame_to.reset_index(inplace=True)
    #del frame['index']
    count = []
    for i in range(len(frame_to)):
        if(pd.isnull(frame_to[field_set][i])):
            count.append(np.nan)
        else: 
            count.append(casecounts[frame_to[field_set][i]])
    frame_to[u'co_freq']= count
    frame_to = frame_to[frame_to[field_set].notnull()]
    frame_to.drop_duplicates(inplace=True)
    frame_to.sort_index(by=[field1, u'co_freq', field2], ascending=False, inplace=True)
    
    frame_to.set_index([field1, field2], inplace=True)
    del frame_to[field_set]
    return frame_to

