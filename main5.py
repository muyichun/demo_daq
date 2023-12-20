import nidaqmx
from nidaqmx.constants import AcquisitionType, Edge
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


# 更新函数，每次调用更新 y 数据
def update(frame, arg1):
    # 读取NI_DAQMX
    with nidaqmx.Task() as task:
        # 选择指定串口
        task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
        task.timing.cfg_samp_clk_timing(2E+6, u'', Edge.FALLING, AcquisitionType.CONTINUOUS)
        task.triggers.start_trigger.cfg_dig_edge_start_trig("/Dev1/PFI0", Edge.FALLING)
        # 实时采集并绘图采集点
        y_axis_amplitude_change = np.round(task.read(number_of_samples_per_channel=COLLECTION_QUANTITY), 5)
        line.set_ydata(y_axis_amplitude_change)
        return line,


# 设置动画
ani = FuncAnimation(fig, update, fargs=(3,), interval=100, cache_frame_data=False, repeat=False, blit=True)
# 展示界面
plt.show()
