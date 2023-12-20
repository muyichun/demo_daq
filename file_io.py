import nidaqmx
import numpy as np
import pandas as pd
from pylab import *
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号




df = pd.read_excel('C:/Users/yangd/Desktop/pulse_2kHZ.xlsx')
COLLECTION_QUANTITY = 5000
x_axis_time = np.array(df['Time - Plot 0'])
y_axis_amplitude = np.array(df['Amplitude - Plot 0'])

#绘图
plt.figure(figsize=(12.8, 7.2))
plt.plot(x_axis_time, y_axis_amplitude)
plt.ylim((-1.2, 1.2))
plt.yticks([-1.2, -1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.title("daq采集信号")
plt.show()