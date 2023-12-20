import nidaqmx
from pylab import *
from matplotlib.animation import FuncAnimation
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号

# 定义初始常量
COLLECTION_QUANTITY = 5000
x_axis_time = [i for i in range(COLLECTION_QUANTITY)]
y_axis_amplitude = np.zeros(COLLECTION_QUANTITY)

# 画布基本信息
fig = plt.figure(figsize=(12.8, 7.2))
# ax = plt.subplots()
line, = plt.plot(x_axis_time, y_axis_amplitude)
plt.ylim((-1.2, 1.2))
plt.yticks([-1.2,-1.0,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1.0,1.2])
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.title("daq采集信号")




with nidaqmx.Task() as task:
    # 选择指定串口
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    # 实时采集并绘图采集点
    y_axis_amplitude_change = np.round(task.read(number_of_samples_per_channel=COLLECTION_QUANTITY), 5)
    print( task.triggers.start_trigger )
    print(task.triggers.pause_trigger)

# 展示界面
plt.show()
