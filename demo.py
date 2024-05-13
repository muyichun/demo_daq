from datetime import datetime
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
from scipy import signal
from scipy.signal import find_peaks, peak_prominences
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号
__author__ = "Jing Xu"

'''
改成1个波形，用子线程更新展示
'''
class WaveformGUI:
    phase_shift = 0
    amp_range = 0
    amp_val = 0
    time_index = 0

    index = 0
    xxx1 = np.array
    xxx2 = np.array
    xxx3 = np.array
    def amplitude_correction(self, data, mod_freq, sample_rate):
        data_f = np.fft.rfft(data)
        main_sine_ind = int(mod_freq * len(data) / sample_rate)
        main_sine_f = np.zeros_like(data_f)
        main_sine_f[0] = data_f[0]
        main_sine_f[main_sine_ind] = data_f[main_sine_ind]
        main_sine = np.fft.irfft(main_sine_f)
        data_corr = data - main_sine
        return data_corr

    def generate_carrier(self, data, phase0, demod_ph_carr_amp):
        phi0 = np.deg2rad(phase0)
        sec_harm_amp = harm_amp
        sec_harm_phase = np.deg2rad(harm_phase)  # rad
        num_T = int(len(data) / mod_table_length)
        w_T = np.linspace(0, 2 * np.pi * (mod_table_length - 1) / mod_table_length, mod_table_length)
        argument_T = demod_ph_carr_amp * (np.sin(w_T - phi0) + sec_harm_amp * np.sin(2 * w_T - phi0 - sec_harm_phase))
        argument = np.tile(argument_T, int(num_T))
        return np.cos(argument) + 1j * np.sin(argument)

    def generate_window(self, data, phase0, sigma=0.0225):
        t = np.linspace(0, (len(data) - 1) / sample_rate, len(data))
        T = 1 / mod_freq
        phi0 = np.deg2rad(phase0)
        num_T = int(len(data) / mod_table_length)
        win = np.array([])
        t0 = phi0 / (2 * np.pi * mod_freq)
        win_T0 = np.exp(-0.5 * ((t[0:int(mod_table_length / 2)] - t0) / (sigma * T)) ** 2)
        win_T1 = win_T0 + np.exp(-0.5 * ((t[0:int(mod_table_length / 2)] - t0 - T / 2) / (sigma * T)) ** 2)
        win_T = win_T1 + np.exp(-0.5 * ((t[0:int(mod_table_length / 2)] - t0 + T / 2) / (sigma * T)) ** 2)
        win = np.tile(win_T, int(num_T * 2))
        return win

    def get_range_view(self, data, dpca_min=1, dpca_max=150, res=1, sigma=0.05, stop_flag=None):
        dpca_range = np.arange(dpca_min, dpca_max, float(res))
        dpca_amp = np.zeros_like(dpca_range)
        window = self.generate_window(data, self.phase_shift, sigma=sigma)
        i = 0
        for dpca in dpca_range:  # dpca sweep
            if stop_flag is not None:
                if stop_flag[0]:
                    break
            carrier = self.generate_carrier(data, self.phase_shift, dpca)
            q = data * carrier * window
            dpca_amp[i] = np.abs(np.sum(q)) / (len(data) / mod_table_length)
            i += 1
        return dpca_range, dpca_amp

    def calc_map(self, data, dpca_min=20, dpca_max=150, dpca_res=1, sigma=0.05,
                 phase_delay_min=80, phase_delay_max=110, phase_delay_res=0.1, stop_flag=None):
        dpca_range = np.arange(dpca_min, dpca_max, float(dpca_res))
        phase_delay_range = np.arange(phase_delay_min, phase_delay_max, float(phase_delay_res))

        map_2d = np.zeros((len(dpca_range), len(phase_delay_range)))
        j = 0
        for ph in phase_delay_range:  # phase delay sweep
            if stop_flag is not None:
                if stop_flag[0]:
                    break
            i = 0
            window = self.generate_window(data, ph, sigma)
            for dpca in dpca_range:  # amplitude sweep
                if stop_flag is not None:
                    if stop_flag[0]:
                        break
                carrier = self.generate_carrier(data, ph, dpca)
                q = data * carrier * window
                map_2d[i, j] = np.abs(np.sum(q)) / (len(data) / mod_table_length)
                i += 1
            j += 1
        return phase_delay_range, dpca_range, map_2d

    def get_peak_positions(self, dpca_range=None, dpca_amp=None, threshold=10):

        dpca_amp_ = np.copy(dpca_amp)
        dpca_amp_[np.nonzero(dpca_amp_ < max(dpca_amp_) * threshold / 100)] = None

        dpca_map_diff = np.diff(np.log(dpca_amp_))
        dpca_range = np.array(dpca_range) + ((dpca_range[1] - dpca_range[0]) / 2)

        zero_cross_index = []
        for i in range(len(dpca_map_diff) - 1):
            if dpca_map_diff[i + 1] < 0 and dpca_map_diff[i] > 0:
                zero_cross_index.append(i)

        peak_position = []
        for i in zero_cross_index:
            peak_line = dpca_map_diff[i:i + 2]
            peak_range = dpca_range[i:i + 2]
            pp = self.find_zero_cross(peak_range, peak_line)
            peak_position.append(pp)

        return peak_position

    def find_zero_cross(self, x, y):
        # y=kx+m
        k = (y[1] - y[0]) / (x[1] - x[0])
        m = y[0] - k * x[0]
        x0 = -m / k
        return x0

    def demodulate_phase(self, data, range_channel, sigma=0.0225):
        carrier = self.generate_carrier(data, self.phase_shift, range_channel)
        window = self.generate_window(data, self.phase_shift, sigma=sigma)
        q = data * carrier * window
        q_filtered = self.lowpass_filter(q)
        q_filtered = self.average(q_filtered)
        phase = np.unwrap(np.angle(q_filtered))
        return phase

    def lowpass_filter(self, x):
        cutoff_hz = mod_freq / 2
        sos = signal.butter(3, cutoff_hz, 'low', fs=sample_rate, output='sos')
        filtered_x = signal.sosfiltfilt(sos, x)
        return filtered_x
    def average(self, x):
        x_reshape = np.reshape(x, (-1, mod_table_length))
        filtered_x = np.mean(x_reshape, axis=1)
        return filtered_x

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
                        y_axis_amplitude_change1 = task.read(number_of_samples_per_channel=self.collection_quantity)
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
                    task.timing.cfg_samp_clk_timing(sample_rate, "", active_edge, AcquisitionType.CONTINUOUS)
                    task.triggers.start_trigger.cfg_dig_edge_start_trig(self.s_t_s_i.get(), active_edge)
                    # 实时采集并绘图采集点
                    y_axis_amplitude_change1 = task.read(number_of_samples_per_channel=self.collection_quantity)
                    # 在主线程中更新图形以避免与Tkinter GUI冲突
                    self.master.after(0, self.redraw1(y_axis_amplitude_change1))
        # stop清零复原
        self.master.after(0, self.redraw1(np.zeros(self.collection_quantity)))


    def redraw1(self, y_axis_amplitude_change1):
        # 首次采集需要预处理
        if self.first_flag:
            self.first_flag = False
            # 第二张图
            self.line2.set_ydata(y_axis_amplitude_change1)
            self.ax2.relim()  # 重新计算数据边界
            # 第三张图
            data_corr = self.amplitude_correction(y_axis_amplitude_change1, mod_freq, sample_rate)
            phase_delay_range, dpca_range, map_values = self.calc_map(y_axis_amplitude_change1, dpca_min=5, dpca_max=80, dpca_res=1,
                                                                 sigma=0.07,
                                                                 phase_delay_min=60, phase_delay_max=180,
                                                                 phase_delay_res=1)
            dx = (phase_delay_range[1] - phase_delay_range[0]) / 2.
            dy = (dpca_range[1] - dpca_range[0]) / 2.
            extent = [phase_delay_range[0] - dx, phase_delay_range[-1] + dx, dpca_range[-1] + dy, dpca_range[0] - dy]
            self.ax3.set_xlabel('Phase Delay / ...° ')
            self.ax3.set_ylabel('Demodulation Phase Carrier Amplitude / rad')
            self.ax3.imshow(map_values / np.max(map_values), extent=extent, aspect='auto')
            # 第四张图
            sum_map = np.sum(map_values, axis=0)
            peak_indexes = signal.argrelextrema(sum_map, np.greater)
            peak_indexes = peak_indexes[0]
            print(peak_indexes)
            peaks, _ = find_peaks(sum_map)
            prominences = peak_prominences(sum_map, peaks)[0]
            prominent_peak_index = peaks[np.argmax(prominences)]  # Index of the most prominent peak
            index = prominent_peak_index
            x_ver = [index, index]
            y_ver = [0, sum_map.max()]
            self.ax4.plot(sum_map)
            self.ax4.plot(x_ver, y_ver)
            # 第五张图
            self.phase_shift = phase_delay_range[index]
            self.amp_range, self.amp_val = self.get_range_view(data_corr, dpca_min=5, dpca_max=180, res=0.1, sigma=0.05)
            self.ax5.plot(self.amp_range, self.amp_val)
            self.ax5.set_xlabel('Demodulation Phase Carrier Amplitude / rad')
            self.ax5.set_ylabel('Amplitude / a.u.')
        # 第一张实时采集图
        self.line1.set_ydata(y_axis_amplitude_change1)
        self.ax1.relim()  # 重新计算数据边界

        # 第六张实时距离变化
        peak_positions = self.get_peak_positions(self.amp_range, self.amp_val, threshold=0.5)

        data_all_corr = self.amplitude_correction(y_axis_amplitude_change1, mod_freq, sample_rate)
        phase = self.demodulate_phase(data_all_corr, range_channel=peak_positions[0])

        wavelength = 1550
        n = 1.0
        path = phase * wavelength / (2 * np.pi * 2 * n)
        # ##plot displacement in micrometer
        displacement = path / 2
        # self.ax6.clear()
        self.ax6.scatter(self.time_index * 1/mod_freq, displacement / 1e3)
        self.time_index += 1
        self.ax6.set_ylabel(r"Displacement [$\mu$m]")
        self.ax6.set_xlabel('Time [s]')
        self.ax6.set_ylim((-2500, 2500))
        # self.ax6.set_yticks([-1.2, -1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])

        self.canvas.draw_idle()  # 绘制新的图形
        # self.ax1.autoscale_view()  # 自动调整坐标轴的缩放

    def __init__(self, master):
        self.master = master
        self.master.title('daq采集信号')
        self.collection_quantity = COLLECTION_QUANTITY
        self.chunk_size = (1, COLLECTION_QUANTITY)

        # 1. 创建 a frame for matplotlib canvas
        fig_frame = tk.Frame(self.master)
        fig_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.fig = plt.figure(figsize=(10.8, 7.2), dpi=100)
        self.ax1 = self.fig.add_subplot(231)
        self.ax2 = self.fig.add_subplot(232)
        self.ax3 = self.fig.add_subplot(233)
        self.ax4 = self.fig.add_subplot(234)
        self.ax5 = self.fig.add_subplot(235)
        self.ax6 = self.fig.add_subplot(236)

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
            # 图1，初始坐标轴
            self.first_flag = True
            self.collection_quantity = int(self.s_p_c_i.get())
            self.chunk_size = (1, self.collection_quantity)
            x = [i for i in range(self.collection_quantity)]
            y = np.zeros(self.collection_quantity)
            # 重绘图形
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            self.ax4.clear()
            self.ax5.clear()
            self.ax6.clear()
            self.line1, = self.ax1.plot(x, y, color='blue', linewidth=1)
            self.ax1.set_xlabel('Time')
            self.ax1.set_ylabel('Amplitude')
            self.line2, = self.ax2.plot(x, y, color='blue', linewidth=1)
            # self.line6, = self.ax2.plot(x, y, color='blue', linewidth=1)
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
    sample_rate = 2e6
    mod_freq = 5e3
    mod_table_length = int(sample_rate / mod_freq)
    harm_amp = 0
    harm_phase = 0

    COLLECTION_QUANTITY = mod_table_length
    CHUNK_SIZE = (1, COLLECTION_QUANTITY)
    TRIGGER_EDGE = [Edge.RISING, Edge.FALLING]
    # 展示GUI界面
    root = tk.Tk()
    app = WaveformGUI(root)
    root.mainloop()