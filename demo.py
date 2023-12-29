import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

class WaveformGUI:
    def __init__(self, master):
        self.master = master
        self.master.title('Waveform Display')

        # 创建一个专门用来放置matplotlib画布的frame
        fig_frame = tk.Frame(master)
        fig_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # 创建figure并添加两个子图
        self.fig = plt.figure(figsize=(5, 8), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)

        # 假设已经绘制了两个波形到ax1和ax2上（这里省略具体绘图代码）

        # 将matplotlib图形转换为可以在Tkinter中显示的画布，并将其添加到fig_frame中
        self.canvas = FigureCanvasTkAgg(self.fig, master=fig_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # 创建一个专门用来放置输入框和按钮的frame
        control_frame = tk.Frame(master)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建四个输入框
        self.input_box1 = tk.Entry(control_frame)
        self.input_box1.pack()

        self.input_box2 = tk.Entry(control_frame)
        self.input_box2.pack()

        self.input_box3 = tk.Entry(control_frame)
        self.input_box3.pack()

        self.input_box4 = tk.Entry(control_frame)
        self.input_box4.pack()

        # 创建两个按钮
        button1 = tk.Button(control_frame, text="Button 1", command=self.button1_clicked)
        button1.pack()

        button2 = tk.Button(control_frame, text="Button 2", command=self.button2_clicked)
        button2.pack()

    def button1_clicked(self):
        pass

    def button2_clicked(self):
        pass

root = tk.Tk()
app = WaveformGUI(root)
root.mainloop()