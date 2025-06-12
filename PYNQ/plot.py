import numpy as np
import time
import threading
import queue
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class LiveECGPlotter:
    def __init__(self, window_size=512, interval=0.01):
        self.window_size = window_size
        self.interval = interval  # seconds
        self.buffer = np.zeros(self.window_size, dtype=float)
        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = None

        # Setup matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(np.arange(self.window_size), self.buffer)
        self.ax.set_ylim(-100, 100)
        self.ax.set_xlim(0, self.window_size)
        self.ax.set_title("ECG Live Plot")
        self.ax.set_xlabel("Campioni")
        self.ax.set_ylabel("Ampiezza")
        plt.ion()
        plt.show()
        self.fig.canvas.draw()
        self.bg = self.fig.canvas.copy_from_bbox(self.ax.bbox)

    def add_samples(self, samples):
        for s in samples:
            self.queue.put(s)

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._update_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()
            print("Live plot fermato.")

    
    def update_plot_once(self, max_samples=32):
        updated = False
        samples_consumed = 0
        try:
            while samples_consumed < max_samples:
                sample = self.queue.get_nowait()
                self.buffer = np.roll(self.buffer, -1)
                self.buffer[-1] = sample
                updated = True
                samples_consumed += 1
        except queue.Empty:
            pass

        if updated:
            self.line.set_ydata(self.buffer)
            self.fig.canvas.draw_idle()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

            
    def _update_loop(self):
        while not self.stop_event.is_set():
            self.update_plot_once(max_samples=32)  
            time.sleep(self.interval)



