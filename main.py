import numpy as np
import matplotlib.pyplot as plt
import h5py
import time
import scipy.signal as signal
from scipy import signal
import statsmodels.api as sm
from scipy.signal import find_peaks, peak_prominences

def amplitude_correction(data, mod_freq, sample_rate):
    data_f = np.fft.rfft(data)
    main_sine_ind = int(mod_freq*len(data)/sample_rate)
    main_sine_f = np.zeros_like(data_f)
    main_sine_f[0] = data_f[0]
    main_sine_f[main_sine_ind] = data_f[main_sine_ind]
    main_sine = np.fft.irfft(main_sine_f)
    data_corr = data - main_sine
    return data_corr
def generate_carrier(data, phase0, demod_ph_carr_amp):
    phi0 = np.deg2rad(phase0)
    sec_harm_amp = harm_amp
    sec_harm_phase = np.deg2rad(harm_phase)  # rad
    num_T = int(len(data) / mod_table_length)
    w_T = np.linspace(0, 2 * np.pi * (mod_table_length - 1) / mod_table_length, mod_table_length)
    argument_T = demod_ph_carr_amp * (np.sin(w_T - phi0) + sec_harm_amp * np.sin(2 * w_T - phi0 - sec_harm_phase))
    argument = np.tile(argument_T, int(num_T))
    return np.cos(argument) + 1j * np.sin(argument)


def generate_window(data, phase0, sigma=0.0225):

    t = np.linspace(0, (len(data)-1)/sample_rate, len(data))
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


def get_range_view(data, dpca_min=1, dpca_max=150, res=1, sigma=0.05, stop_flag=None):
    dpca_range = np.arange(dpca_min, dpca_max, float(res))
    dpca_amp = np.zeros_like(dpca_range)
    window = generate_window(data, phase_shift, sigma=sigma)
    i = 0
    for dpca in dpca_range:     # dpca sweep
        if stop_flag is not None:
            if stop_flag[0]:
                break
        carrier = generate_carrier(data,phase_shift, dpca)
        q = data*carrier*window
        dpca_amp[i] = np.abs(np.sum(q)) / (len(data) / mod_table_length)
        i += 1
    return dpca_range, dpca_amp

def calc_map(data, dpca_min=20, dpca_max=150, dpca_res=1, sigma=0.05,
                 phase_delay_min=80, phase_delay_max=110, phase_delay_res=0.1, stop_flag=None):
    dpca_range = np.arange(dpca_min, dpca_max, float(dpca_res))
    phase_delay_range = np.arange(phase_delay_min, phase_delay_max, float(phase_delay_res))

    map_2d = np.zeros((len(dpca_range), len(phase_delay_range)))
    j = 0
    for ph in phase_delay_range:    # phase delay sweep
        if stop_flag is not None:
            if stop_flag[0]:
                break
        i = 0
        window = generate_window(data, ph, sigma=sigma)
        for dpca in dpca_range:  # amplitude sweep
            if stop_flag is not None:
                if stop_flag[0]:
                    break
            carrier = generate_carrier(data, ph, dpca)
            q = data * carrier * window
            map_2d[i, j] = np.abs(np.sum(q)) / (len(data) / mod_table_length)
            i += 1
        j += 1

    return phase_delay_range, dpca_range, map_2d
def get_peak_positions(dpca_range=None, dpca_amp=None, threshold=10):

    dpca_amp_ = np.copy(dpca_amp)
    dpca_amp_[np.nonzero(dpca_amp_ < max(dpca_amp_) * threshold/100)] = None

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
        pp = find_zero_cross(peak_range, peak_line)
        peak_position.append(pp)

    return peak_position

def find_zero_cross(x, y):
    # y=kx+m
    k = (y[1] - y[0]) / (x[1] - x[0])
    m = y[0] - k * x[0]
    x0 = -m / k
    return x0
def demodulate_phase(data, range_channel, sigma=0.0225):
    carrier = generate_carrier(data, phase_shift, range_channel)
    window = generate_window(data, phase_shift, sigma=sigma)
    q = data*carrier*window
    q_filtered = lowpass_filter(q)
    q_filtered = average(q_filtered)
    phase = np.unwrap(np.angle(q_filtered))
    return phase

def lowpass_filter(x):
    cutoff_hz = mod_freq / 2
    sos = signal.butter(3, cutoff_hz, 'low', fs=sample_rate, output='sos')
    filtered_x = signal.sosfiltfilt(sos, x)
    return filtered_x

def average(x):
    x_reshape = np.reshape(x, (-1, mod_table_length))
    filtered_x = np.mean(x_reshape, axis=1)
    return filtered_x





# 1. 初始化参数
sample_rate = 2e6
mod_freq = 5e3
mod_table_length = int(sample_rate/mod_freq)
# 2. 读h5文件
# data_name = r'D:\HGY_DATA\test_daq\displacement_test_1_5khz_2mm.hdf5'
# data_name = r'D:\HGY_DATA\test_daq\bak_displacement_test_1_5khz_2mm.hdf5'
data_name = r'D:\HGY_DATA\test_daq\xj.h5'
with h5py.File(data_name, 'r') as f:
    dataset_name = list(f.keys())
    my_data_raw = [None] * len(dataset_name)
    for num_dset in range(len(dataset_name)):
        my_data_raw [num_dset] = f.get(dataset_name[num_dset])[()]
    f.close()
# [可选]打印原始波形
# data_to_run = my_data_raw[1]
# test_data=data_to_run[0]
# print(data_to_run.shape)
# plt.plot(test_data)
# plt.show()
# 3. 单独计算第一个点：amplitude_correction
data_to_run = my_data_raw[1]
test_data = data_to_run[0]
data_corr = amplitude_correction(test_data,mod_freq,sample_rate)
# 4. set processing parameters
harm_amp = 0
harm_phase = 0
phase_delay_range, dpca_range, map_values = calc_map(test_data, dpca_min=5, dpca_max=80, dpca_res=1, sigma=0.07,
                                                         phase_delay_min=60, phase_delay_max=180, phase_delay_res=1)
# dx = (phase_delay_range[1] - phase_delay_range[0]) / 2.
# dy = (dpca_range[1] - dpca_range[0]) / 2.
# extent = [phase_delay_range[0] - dx, phase_delay_range[-1] + dx, dpca_range[-1] + dy, dpca_range[0] - dy]
# plt.imshow(map_values / np.max(map_values), extent=extent, aspect='auto')
# plt.ylabel('Demodulation Phase Carrier Amplitude / rad')
# plt.xlabel('Phase Delay / ...° ')
# plt.colorbar()
# plt.show()
# 5. 找到所有顶点，并拿到最对称的顶点线：peek line
sum_map = np.sum(map_values, axis=0)
data_y = sum_map
print(sum_map.shape)
peak_indexes = signal.argrelextrema(data_y, np.greater)
peak_indexes = peak_indexes[0]
print(peak_indexes)
peaks, _ = find_peaks(sum_map)
prominences = peak_prominences(sum_map, peaks)[0]
prominent_peak_index = peaks[np.argmax(prominences)]  # Index of the most prominent peak
index = prominent_peak_index
# x_ver=[index,index]
# y_ver=[0,sum_map.max()]
# plt.plot(sum_map)
# plt.plot(x_ver,y_ver)
# plt.show()
# exit()
# print(phase_delay_range[peak_indexes[des_ind]])
# 6. 得到phase_shift最关键
phase_shift = phase_delay_range[index]
amp_range, amp_val = get_range_view(data_corr,dpca_min=5, dpca_max=180, res=0.1, sigma=0.05)
# plt.plot(amp_range, amp_val)
# plt.xlabel('Demodulation Phase Carrier Amplitude / rad')
# plt.ylabel('Amplitude / a.u.')
# plt.show()


# 7. 继续相关处理
peak_positions = get_peak_positions(amp_range, amp_val, threshold=0.5)
print('Peaks maximums are at', peak_positions)
# 8. 计算所有数据，相位, 并显示最终结果show in displacement
data_all = np.reshape(data_to_run, data_to_run.shape[0]*data_to_run.shape[1])
data_all_corr = amplitude_correction(data_all, mod_freq, sample_rate)
phase = demodulate_phase(data_all_corr, range_channel=peak_positions[0])
# print(len(data_to_run))

# phase_list = []
# phase_tmp = []
# for i in range(1000):
#     d = amplitude_correction(data_to_run[i], mod_freq, sample_rate)
#     phase = demodulate_phase(d, range_channel = peak_positions[0])
#     phase_list.extend(phase)
#     phase_tmp = np.unwrap(phase_list)

t = np.linspace(0, len(phase) / mod_freq, len(phase))

wavelength = 1550
n = 1.0
path = phase*wavelength/(2*np.pi*2*n)
# ##plot displacement in micrometer
displacement =path/2
plt.plot(t, displacement/1e3)
plt.ylabel(r"Displacement [$\mu$m]")
plt.xlabel('Time [s]')
plt.show()