import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np

class WaveformGUI:
    def __init__(self, master):
        self.master = master
        self.master.title('Realtime Waveform')

        self.fig = plt.figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot([], [])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.update()

        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.x_data = []
        self.y_data = []

        self.update_plot()

    def update_plot(self):
        # Generate new data point
        x = np.linspace(0, 2*np.pi, len(self.x_data) + 100)
        y = np.sin(x)

        self.x_data.extend(x[len(self.x_data):])
        self.y_data.extend(y[len(self.y_data):])

        # Update the line with new data
        self.line.set_data(self.x_data, self.y_data)

        # Re-scale the axes
        self.ax.relim()
        self.ax.autoscale_view()

        # Update the canvas
        self.canvas.draw()

        # Call update_plot again after 100 milliseconds
        self.master.after(100, self.update_plot)


root = tk.Tk()
app = WaveformGUI(root)
root.mainloop()
