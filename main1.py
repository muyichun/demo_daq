import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


class WaveformGUI:
    def __init__(self, master):
        self.master = master
        self.master.title('Waveform Display')

        # Generate sample data
        x1 = np.linspace(0, 2*np.pi, 100)
        y1 = np.sin(x1)

        x2 = np.linspace(-5, 5, 100)
        y2 = np.exp(-x2**2 / 2) / np.sqrt(2 * np.pi)

        # Create the figure and axes
        self.fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(223)

        # Plot the waveforms
        self.line1, = self.ax1.plot(x1, y1, color='blue', linewidth=2)
        self.line2, = self.ax2.plot(x2, y2, color='red', linewidth=2)

        # Set axis labels and limits
        self.ax1.set_xlabel('X-axis 1')
        self.ax1.set_ylabel('Y-axis 1')
        self.ax1.set_xlim([0, 2*np.pi])
        self.ax1.set_ylim([-1.1, 1.1])

        self.ax2.set_xlabel('X-axis 2')
        self.ax2.set_ylabel('Y-axis 2')
        self.ax2.set_xlim([-5, 5])
        self.ax2.set_ylim([0, 1])

        # Create the canvas and pack it into the GUI
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create buttons
        self.button1 = tk.Button(master, text="Button 1", command=self.button1_clicked)
        self.button1.pack(side=tk.LEFT)

        self.button2 = tk.Button(master, text="Button 2", command=self.button2_clicked)
        self.button2.pack(side=tk.LEFT)

        # Create input boxes
        self.input_box1 = tk.Entry(master)
        self.input_box1.pack(side=tk.LEFT)

        self.input_box2 = tk.Entry(master)
        self.input_box2.pack(side=tk.LEFT)

        self.input_box3 = tk.Entry(master)
        self.input_box3.pack(side=tk.LEFT)

        self.input_box4 = tk.Entry(master)
        self.input_box4.pack(side=tk.LEFT)

    def button1_clicked(self):
        values = [self.input_box1.get(), self.input_box2.get(), self.input_box3.get(), self.input_box4.get()]
        print(f"Button 1 clicked with values: {values}")

    def button2_clicked(self):
        value1 = self.input_box1.get()
        value2 = self.input_box2.get()
        print(f"Button 2 clicked with values: {value1}, {value2}")


root = tk.Tk()
app = WaveformGUI(root)
root.mainloop()
