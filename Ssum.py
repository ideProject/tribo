# -*- coding: utf-8 -*-
import numpy as np
from pandas import DataFrame
class SVD:
    def SVD_run(self, frame):
        #特異値分解
        fmat = frame.as_matrix()
        U, S, V = np.linalg.svd(fmat)
        Uframe = DataFrame(U, index = frame.index)
        Vframe = DataFrame(V, index = frame.columns)
        Sframe = DataFrame(S)

        '''
        a=Uframe.index
        b=[i.decode('utf_8') for i in a]
        #a2=Vframe.index.get_level_values(1)
        a2=Vframe.index.get_level_values(0)
        b2 = [i.decode('utf_8') for i in a2]
        '''

        UVSframe = [Uframe, Vframe, Sframe]
        return UVSframe

    def sf(self, Sframe):
        Ssum = 0
        for i in range(len(Sframe)):
            Ssum = Ssum + Sframe[0][i]

        Sleft=0
        Sright=Ssum
        for i in range(len(Sframe)):
            Sleft = Sleft+Sframe[0][i]
            Sright= Sright-Sframe[0][i]
            print 'Sleft= %s' %Sleft
            print 'Sright= %s' % Sright
            if Sleft>Sright:
                print i+1
                return i+1

'''
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
result1 = linkage(Uframe.ix[:,:sf(Sframe)-1], metric = 'euclidean', method = 'ward')
den=dendrogram(result1,labels=b,leaf_font_size=15,color_threshold=1.0)
plt.title(u'深層格')

clusterN = fcluster(linkage(Uframe.ix[:,:sf(Sframe)-1], metric = 'euclidean', method = 'ward'),1.0,'distance')

show()
'''
