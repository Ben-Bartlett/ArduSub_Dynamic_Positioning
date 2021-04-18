import matplotlib.pyplot as plt
import numpy as np
from numpy import genfromtxt
from mpl_toolkits.mplot3d import Axes3D
import easygui
import sys


'choose depth/heading etc'
filename = easygui.fileopenbox()
try:
    data = genfromtxt(filename, delimiter=',')
except:
    sys.exit()
# arbitrary time
x = list(range(0,len(data)))
# depth at each sample
y = data[:,1]
# target depth
y2 = data[:,3]

plt.figure()
# x y 
# buffer above and below max and min values for asthetic
y_min = min(y) - abs((min(y)/4))
y_max = max(y) + abs((max(y)/4))
plt.axis([0,len(x)-1, y_min ,y_max])
plt.plot(x,y)
plt.plot(x,y2)
plt.show()

