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
chunk_size = (1, length)

# 打开H5文件，如果文件不存在则创建
with h5py.File(f5_path, 'a') as file:
    dataset = file.create_dataset('Imaging data_' + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                        , shape=(0, length)
                        , maxshape=(None, length)
                        , dtype=float32
                        , chunks=chunk_size)
    # 初始化创建字符串属性
    dataset.attrs['Display Time'] = 0
    # 生成新数据
    new_data = (4, 5, 6)
    current_len = len(dataset)
    dataset.resize(current_len + 1, axis=0)
    # 追加写入新数据
    dataset[current_len:] = new_data

    # 模拟循环实时写入
    for i in range(10):
        new_data = (4, 5, 6)
        current_len = len(dataset)
        dataset.resize(current_len + 1, axis=0)
        # 追加写入新数据
        dataset[current_len:] = new_data



