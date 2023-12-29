import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


class WaveformGUI:
    def __init__(self, master):
        self.master = master
        self.master.title('Waveform Display')

        # 1.Create a frame for matplotlib canvas
        fig_frame = tk.Frame(master)
        fig_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Generate sample data and create figure
        x1 = np.linspace(0, 2*np.pi, 100)
        y1 = np.sin(x1)
        x2 = np.linspace(-5, 5, 100)
        y2 = np.exp(-x2**2 / 2) / np.sqrt(2 * np.pi)

        self.fig = plt.figure(figsize=(10.8, 7.2), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        self.line1, = self.ax1.plot(x1, y1, color='blue', linewidth=2)
        self.line2, = self.ax2.plot(x2, y2, color='red', linewidth=2)
        # Set axis labels and limits
        self.ax1.set_xlabel('Time')
        self.ax1.set_ylabel('Amplitude')
        self.ax1.set_xlim([0, 2*np.pi])
        self.ax1.set_ylim((-1.2, 1.2))
        self.ax1.set_yticks([-1.2, -1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])

        self.ax2.set_xlabel('Time')
        self.ax2.set_ylabel('Amplitude')
        self.ax2.set_xlim([-5, 5])
        self.ax2.set_ylim((-1.2, 1.2))
        self.ax2.set_yticks([-1.2, -1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])

        # Add matplotlib canvas to the frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=fig_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # 2.Create a frame for input boxes and buttons
        control_frame = tk.Frame(master)
        control_frame.pack(side=tk.TOP, fill=tk.Y)
        separator1 = tk.Label(control_frame, text="Custom", bd=1, pady=10, relief=tk.SUNKEN, bg="gray")
        # Create four input boxes
        self.p_c_l1 = tk.Label(control_frame, text="Physical Channels 1", fg="blue")
        self.p_c_i1 = ttk.Combobox(control_frame, values=["Dev1/ai0"],state='readonly')
        self.p_c_i1.current(0)

        self.p_c_l2 = tk.Label(control_frame, text="Physical Channels 2", fg="red")
        self.p_c_i2 = ttk.Combobox(control_frame, values=["Dev1/ai1"],state='readonly')
        self.p_c_i2.current(0)

        self.s_p_c_l = tk.Label(control_frame, text="Samples Per Channel")
        self.s_p_c_i = tk.Entry(control_frame)
        self.s_p_c_i.insert(0,"5000")

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
        self.p_c_l2.pack()
        self.p_c_i2.pack()
        self.s_p_c_l.pack()
        self.s_p_c_i.pack()
        self.s_e_l.pack()
        self.s_e_i.pack()
        self.s_t_s_l.pack()
        self.s_t_s_i.pack()
        separator2.pack(fill=tk.X)

        self.s_p_b = tk.Button(control_frame, text="Select a save path", command=self.button1_clicked)
        self.s_p_i = tk.Entry(control_frame)
        self.s_p_i.insert(0,"5000")
        self.s_p_b.pack()
        self.s_p_i.pack()

        self.radio_mode = tk.StringVar(value="Overwrite")
        self.option1 = tk.Radiobutton(control_frame, text="Overwrite", variable=self.radio_mode, value="Overwrite")
        self.option2 = tk.Radiobutton(control_frame, text="Append", variable=self.radio_mode, value="Append")
        # radio_var.trace("w", on_selection_change)
        self.s_b = tk.Button(control_frame, text="Yes", command=self.button3_clicked)
        self.option1.pack()
        self.option2.pack()
        self.s_b.pack()

    def button1_clicked(self):
        pass

    def button2_clicked(self):
        pass

    def button3_clicked(self):
        pass


root = tk.Tk()
app = WaveformGUI(root)
root.mainloop()