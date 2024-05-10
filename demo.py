import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
import nidaqmx
from nidaqmx.constants import Edge,AcquisitionType
import threading
import time
import h5py
import os
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号
__author__ = "Jing Xu"

'''
改成1个波形，用子线程更新展示
'''
class WaveformGUI:
    def update_waveform1(self):
        # 是否把数据导出h5文件
        if self.s_b.cget('text') == 'Deny':
            # 判断是覆盖 or 追加，如果是覆盖，直接删除文件
            if self.write_mode.get() == 'Overwrite' and os.path.exists(self.h5_input.get()):
                os.remove(self.h5_input.get())
            with h5py.File(self.h5_input.get(), 'a') as file:
                dataset = file.create_dataset(
                    'Imaging data_' + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                    , shape=(0, self.collection_quantity)
                    , maxshape=(None, self.collection_quantity)
                    , dtype=np.float32
                    , chunks=self.chunk_size)
                # 初始化创建字符串属性
                dataset.attrs['Display Time'] = 0
                # 实时更新波形
                while not self.stop_event.is_set():
                    # 更新数据（这里仅作示例，实际应根据你的需求获取实时数据）
                    with nidaqmx.Task() as task:
                        # 选择指定串口
                        task.ai_channels.add_ai_voltage_chan(self.p_c_i1.get())
                        # 选择时钟同步串口
                        active_edge = TRIGGER_EDGE[self.s_e_i['values'].index(self.s_e_i.get())]
                        task.timing.cfg_samp_clk_timing(2E+6, "", active_edge, AcquisitionType.CONTINUOUS)
                        task.triggers.start_trigger.cfg_dig_edge_start_trig(self.s_t_s_i.get(), active_edge)
                        # 实时采集并绘图采集点
                        y_axis_amplitude_change1 = np.round(task.read(number_of_samples_per_channel=self.collection_quantity), 5)
                        # 追加写入新数据
                        current_len = len(dataset)
                        # print("写入中：", current_len)
                        dataset.resize(current_len + 1, axis=0)
                        dataset[current_len:] = y_axis_amplitude_change1
                        # 在主线程中更新图形以避免与Tkinter GUI冲突
                        self.master.after(0, self.redraw1(y_axis_amplitude_change1))
        else:
            # 实时更新波形
            while not self.stop_event.is_set():
                # 更新数据（这里仅作示例，实际应根据你的需求获取实时数据）
                with nidaqmx.Task() as task:
                    # 选择指定串口
                    task.ai_channels.add_ai_voltage_chan(self.p_c_i1.get())
                    # 选择时钟同步串口
                    active_edge = TRIGGER_EDGE[self.s_e_i['values'].index(self.s_e_i.get())]
                    task.timing.cfg_samp_clk_timing(2E+6, "", active_edge, AcquisitionType.CONTINUOUS)
                    task.triggers.start_trigger.cfg_dig_edge_start_trig(self.s_t_s_i.get(), active_edge)
                    # 实时采集并绘图采集点
                    y_axis_amplitude_change1 = np.round(task.read(number_of_samples_per_channel=self.collection_quantity), 5)
                    # 在主线程中更新图形以避免与Tkinter GUI冲突
                    self.master.after(0, self.redraw1(y_axis_amplitude_change1))
        # stop清零复原
        self.master.after(0, self.redraw1(np.zeros(self.collection_quantity)))


    def redraw1(self, y_axis_amplitude_change1):
        self.line1.set_ydata(y_axis_amplitude_change1)
        self.canvas.draw_idle()  # 绘制新的图形


    def __init__(self, master):
        self.master = master
        self.master.title('daq采集信号')
        self.collection_quantity = COLLECTION_QUANTITY
        self.chunk_size = (1, COLLECTION_QUANTITY)

        # 1. 创建 a frame for matplotlib canvas
        fig_frame = tk.Frame(self.master)
        fig_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        x1 = [i for i in range(COLLECTION_QUANTITY)]
        y1 = np.zeros(COLLECTION_QUANTITY)

        self.fig = plt.figure(figsize=(10.8, 7.2), dpi=100)
        self.ax1 = self.fig.add_subplot(111)
        self.line1, = self.ax1.plot(x1, y1, color='blue', linewidth=2)
        # Set axis labels and limits
        self.ax1.set_xlabel('Time')
        self.ax1.set_ylabel('Amplitude')
        self.ax1.set_ylim((0, 2.2))
        self.ax1.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2])
        # Add matplotlib canvas to the frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=fig_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # 2. Create a frame for input boxes and buttons
        control_frame = tk.Frame(master)
        control_frame.pack(side=tk.TOP, fill=tk.Y)
        separator1 = tk.Label(control_frame, text="Custom", bd=1, pady=10, relief=tk.SUNKEN, bg="gray")
        # Create four input boxes
        self.p_c_l1 = tk.Label(control_frame, text="Physical Channels 1", fg="blue")
        self.p_c_i1 = ttk.Combobox(control_frame, values=["Dev1/ai0", "Dev1/ai1"], state='readonly')
        self.p_c_i1.current(0)

        self.s_p_c_l = tk.Label(control_frame, text="Samples Per Channel")
        self.s_p_c_i = tk.Entry(control_frame)
        self.s_p_c_i.insert(0,"400")

        self.s_e_l = tk.Label(control_frame, text="Start Edge")
        self.s_e_i = ttk.Combobox(control_frame, values=["Rising", "Falling"],state='readonly')
        self.s_e_i.current(0)

        self.s_t_s_l = tk.Label(control_frame, text="Start Trigger Source")
        self.s_t_s_i = ttk.Combobox(control_frame, values=["/Dev1/PFI0"],state='readonly')
        self.s_t_s_i.current(0)

        separator2 = tk.Label(control_frame, text="Export Imaging Data ?", bd=1, pady=10, relief=tk.SUNKEN, bg="gray")

        separator1.pack(fill=tk.X)
        self.p_c_l1.pack()
        self.p_c_i1.pack()
        self.s_p_c_l.pack()
        self.s_p_c_i.pack()
        self.s_e_l.pack()
        self.s_e_i.pack()
        self.s_t_s_l.pack()
        self.s_t_s_i.pack()
        separator2.pack(fill=tk.X)

        # 用一个新控件，把两个单选按钮放一行
        tmp_frame1 = tk.Frame(control_frame)
        self.h5_button = tk.Button(tmp_frame1, text="...", command=self.choose_h5_clicked)
        self.h5_input = tk.Entry(tmp_frame1)
        self.h5_input.insert(0, "D:/HGY_DATA/test_daq/xj.h5")
        self.h5_button.pack(side=tk.LEFT)
        self.h5_input.pack(side=tk.LEFT)
        tmp_frame1.pack()

        # 用一个新控件，把两个单选按钮放一行
        tmp_frame2 = tk.Frame(control_frame)
        self.write_mode = tk.StringVar(value="Overwrite")
        self.option1 = tk.Radiobutton(tmp_frame2, text="Overwrite", variable=self.write_mode, value="Overwrite")
        self.option2 = tk.Radiobutton(tmp_frame2, text="Append", variable=self.write_mode, value="Append")
        # radio_var.trace("w", on_selection_change)
        self.s_b = tk.Button(control_frame, text="Confirm",fg="green", command=self.export_confirm_clicked)
        self.option1.pack(side=tk.LEFT)
        self.option2.pack(side=tk.LEFT)
        tmp_frame2.pack()
        self.s_b.pack()

        # 启动
        separator3 = tk.Label(control_frame, text="Bootstrap", bd=1, pady=10, relief=tk.SUNKEN, bg="gray")
        separator3.pack(fill=tk.X)
        self.begin_b = tk.Button(control_frame, text="Start", fg="green", command=self.start_clicked)
        self.begin_b.pack()

    def choose_h5_clicked(self):
        file_path = filedialog.askopenfilename(
            parent=root,
            initialdir="D:/HGY_DATA/test_daq/xj.h5",
            title="请选择一个h5文件",
            filetypes=[("hdf5 Files", "*.hdf5"), ("hdf5 Files", "*.h5")]
        )
        if file_path:
            self.h5_input.delete(0, "end")
            self.h5_input.insert(0, file_path)

    def export_confirm_clicked(self):
        if self.s_b.cget('text') == 'Confirm':
            self.s_b.config(text="Deny", fg="red")
            self.option1['state'] = 'disabled'
            self.option2['state'] = 'disabled'
            self.h5_button['state'] = 'disabled'
            self.h5_input['state'] = 'disabled'
        else:
            self.s_b.config(text="Confirm", fg='green')
            self.option1['state'] = 'normal'
            self.option2['state'] = 'normal'
            self.h5_button['state'] = 'normal'
            self.h5_input['state'] = 'normal'

    def start_clicked(self):
        if self.begin_b.cget('text') == 'Start':
            # 配置Custom相关参数
            self.begin_b.config(text="Stop", fg="red")
            self.s_b['state'] = 'disabled'
            self.collection_quantity = int(self.s_p_c_i.get())
            self.chunk_size = (1, self.collection_quantity)
            x = [i for i in range(self.collection_quantity)]
            y = np.zeros(self.collection_quantity)
            # 重绘图形
            self.ax1.clear()
            self.line1, = self.ax1.plot(x, y, color='blue', linewidth=2)
            self.ax1.set_xlabel('Time')
            self.ax1.set_ylabel('Amplitude')
            self.ax1.set_ylim((0, 2.2))
            self.ax1.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2])
            # 创建并启动更新线程
            self.stop_event = threading.Event()
            self.update_thread1 = threading.Thread(target=self.update_waveform1, daemon=True)
            self.update_thread1.start()
        else:
            self.stop_event.set()
            self.begin_b.config(text="Start", fg='green')
            self.s_b['state'] = 'normal'


if __name__ == '__main__':
    # 默认参数
    COLLECTION_QUANTITY = 400
    CHUNK_SIZE = (1, COLLECTION_QUANTITY)
    TRIGGER_EDGE = [Edge.RISING, Edge.FALLING]
    # 展示GUI界面
    root = tk.Tk()
    app = WaveformGUI(root)
    root.mainloop()