# -*- coding: utf-8 -*-
'''        
frame['case']= frame['深層格']+'_'+frame['表層格']
casecounts = frame['case'].value_counts()
frame =frame.reset_index()
del frame['index']
'''

import numpy as np
import pandas as pd
class Count():
    def casecount(self, frame, casecounts):
        count = []
        for i in range(len(frame)):
            if(pd.isnull(frame['case'][i])):
                count.append(np.nan)
            else: 
                count.append(casecounts[frame['case'][i]])
        return count

'''
frame['count']= count
frame =frame[frame['case'].notnull()]
frame=frame.drop_duplicates()
frame2=frame.set_index(['深層格', '表層格'])
del frame2['case']
frame3 =frame2.unstack()
frame3 = frame3.fillna(0)
'''
