import nidaqmx
from pylab import *
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号
# import numpy as np
# import matplotlib.pyplot as plt

COLLECTION_QUANTITY = 500
x_axis_time = np.zeros(COLLECTION_QUANTITY)
y_axis_amplitude = np.zeros(COLLECTION_QUANTITY)
# 读取NI_DAQMX
with nidaqmx.Task() as task:
    # 选择指定串口
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    # 实时采集并绘图采集点
    for i in range(0, COLLECTION_QUANTITY):
        x_axis_time[i] = i
        y_axis_amplitude[i] = np.round(task.read(),5)
        print(y_axis_amplitude[i])

    plt.figure(figsize=(12.8, 7.2))
    plt.plot(x_axis_time, y_axis_amplitude)
    plt.ylim((-1.2, 1.2))
    plt.yticks([-1.2,-1.0,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1.0,1.2])
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.title("daq采集信号")
    plt.show()
