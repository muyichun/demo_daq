import nidaqmx
from nidaqmx.constants import AcquisitionType, Edge
from pylab import *
from matplotlib.animation import FuncAnimation
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号
import time


# str = "xxx" + "_" + time.strftime("%Y_%m_%d__%H_%M_%S", time.localtime())
# print(str)
# print(2**32 - 1)
arr = np.zeros(2)
print(arr)