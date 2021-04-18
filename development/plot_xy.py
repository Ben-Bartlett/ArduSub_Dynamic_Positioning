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

# data = np.round(data, 1)

# arbitrary time
t = list(range(0,len(data)))

# actual x
x_actual = data[:,1]
#actual y
y_actual = data[:,2]

x_commanded = data[:,4]
y_commanded = data[:,6]

fig, (ax1, ax2, ax3) = plt.subplots(3, constrained_layout=True)
fig.suptitle('X and Y')
ax1.plot(t,x_actual)
ax1.plot(t,x_commanded)
ax1.set_title('X(Surge) over time')
ax2.plot(t,y_actual)
ax2.plot(t,y_commanded)
ax2.set_title('Y(Sway) over time')
#X being north or 'up' so more like Y
ax3.plot(y_actual,x_actual)
ax3.plot(y_commanded,x_commanded)
ax3.set_title('X vs Y')
plt.show()
#plt.axis([0,len(x_actual)-1, min(x_actual) - abs((min(x_actual)/4)) ,max(x_actual) + abs((max(x_actual)/4))])


