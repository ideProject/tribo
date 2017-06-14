# -*- coding: utf-8 -*-
from pandas import DataFrame
import pandas as pd
def matome(f):
    frame=DataFrame()
    for i in range(1,6):
        tmpframe=DataFrame(f,columns= ['格%d(深層格)' %i,'格%d(表層格)' %i])
        tmpframe=tmpframe.rename(columns= {'格%d(深層格)' %i:'深層格','格%d(表層格)' %i:'表層格'})
        frame = pd.concat([frame,tmpframe],ignore_index=True)
    return frame
