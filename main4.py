import nidaqmx
import h5py
import os
from pylab import *
from nidaqmx.constants import AcquisitionType, Edge
from matplotlib.animation import FuncAnimation
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号


# 初始化参数：文件路径/采集长度
f5_path = "D:/HGY_DATA/test_daq/xj.h5"
length = 3

# 新建/追加 写文件
if not os.path.exists(f5_path):
    file = h5py.File(f5_path, "w")
else:
    file = h5py.File(f5_path, 'a')

dataset = file.create_dataset('Imaging data_' + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                    , data=[(1,2,3)]
                    , dtype=float32)
new_data = ([4,5,6])
dataset[len(new_data):] = new_data

file.close()

#
# file = h5py.File(path, 'w')
# dataset = file.create_dataset('Imaging data_' + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()), (4, 6), h5py.h5t.STD_I32BE)
# # 创建字符串属性
# dataset.attrs['Display Time'] = 0
# # 创建整型属性
# # attr_data = np.zeros((2,))
# # attr_data[0] = 100
# # attr_data[1] = 200
# # dataset.attrs.create('Display Time', attr_data, (2,), 'i')
# file.close()


