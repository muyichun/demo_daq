import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType, Edge
from pylab import *
from matplotlib.animation import FuncAnimation
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号

# 定义初始常量
COLLECTION_QUANTITY = 5000
x_axis_time = np.array([i for i in range(COLLECTION_QUANTITY)])
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


def query_devices():
    local_system = nidaqmx.system.System.local()
    driver_version = local_system.driver_version
    print('DAQmx {0}.{1}.{2}'.format(driver_version.major_version, driver_version.minor_version,
                                    driver_version.update_version))
    for device in local_system.devices:
        print('Device Name: {0}, Product Category: {1}, Product Type: {2}'.format(
            device.name, device.product_category, device.product_type))


with nidaqmx.Task() as task:
    # 选择指定串口 & TTL
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    task.timing.cfg_samp_clk_timing(2E+6, u'', Edge.RISING, sample_mode=AcquisitionType.CONTINUOUS)
    task.triggers.start_trigger.cfg_dig_edge_start_trig("/Dev1/PFI0", Edge.RISING)
    # task.in_stream.timeout = 200
    # 实时采集并绘图采集点
    y_axis_amplitude_change = np.round(task.read(number_of_samples_per_channel=COLLECTION_QUANTITY), 5)
    line.set_ydata(y_axis_amplitude_change)

# 展示界面
plt.show()
# query_devices()