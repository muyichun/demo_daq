from pylab import *
from matplotlib.animation import FuncAnimation
from datetime import datetime


# 初始化图形
fig, ax = plt.subplots()

x_data = np.arange(0, 10, 0.1)  # 示例 x 轴数据 100个点
line, = ax.plot(x_data, np.sin(x_data))  # 示例 y 轴数据

# 更新函数，每次调用更新 y 数据
def update(frame):
    print(frame)
    y_data = np.sin(x_data + frame / 10.0)
    line.set_ydata(y_data)
    return line,
# 设置动画
ani = FuncAnimation(fig, update, frames=None, interval=100, cache_frame_data=False,repeat=False, blit=True)

# 显示图形
plt.show()