'''
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure();ax = fig.add_subplot(1,1,1)

for i, txt in enumerate(b):
    ax.scatter(Uframe.ix[i,0],Uframe.ix[i,1])
    ax.text(Uframe.ix[i,0],Uframe.ix[i,1],(txt))
'''

#
'''
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


fig = pylab.figure()
ax = Axes3D(fig)
for i, txt in enumerate(b): 
 ax.scatter(Uframe.ix[i,0],Uframe.ix[i,1],Uframe.ix[i,2])
 ax.text(Uframe.ix[i,0],Uframe.ix[i,1],Uframe.ix[i,2],(txt))
'''