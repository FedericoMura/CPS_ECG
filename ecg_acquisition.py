from pynq import MMIO
import threading
import time
import numpy as np
import matplotlib.pyplot as plt

class SpiECG:
    SPICR   = 0x60   # SPI Control Register
    SPISR   = 0x64   # SPI Status  Register (RX empty flag)
    SPI_DTR = 0x68   # Data Transmit Register
    SPI_DRR = 0x6C   # Data Receive  Register
    SPISSR  = 0x70   # Slave-Select   Register

    def __init__(self, overlay, ip_name="axi_quad_spi_0", cs_mask=0xFFFFFFFE, fs=200):
        """
        overlay: instance of already loaded PYNQ Overlay
        ip_name: name of the AXI Quad SPI IP in the overlay
        cs_mask: mask for CS activation
        fs: sampling frequency (Hz)
        """
        self.fs = fs
        self.period = 1.0 / fs
        spi_ip = getattr(overlay, ip_name)
        self.mmio = spi_ip.mmio
        self.cs_mask = cs_mask
        self._init_spi()

    def _init_spi(self):
        # SPI Configuration routine
        self.mmio.write(self.SPICR, 0x86)
        self.mmio.write(self.SPISSR, self.cs_mask)
        time.sleep(0.001)

    def read_one(self):
        self.mmio.write(self.SPI_DTR, 0x0101)
        # wait for RX not empty (bit0 SPISR==1)
        while (self.mmio.read(self.SPISR) & 0x01) == 1:
            pass
        return self.mmio.read(self.SPI_DRR) & 0xFFFF

class ECGAcquisition:
    """
    Double-buffered acquisition from SPI at fs Hz.
    Each buffer of N samples is passed to the callback.
    """
    def __init__(self, overlay, ip_name,
                 buffer_size=200, callback=None,
                 cs_mask=0xFFFFFFFE, fs=200):
        self.spi = SpiECG(overlay, ip_name, cs_mask, fs) # Initialize SPI master
        self.N = buffer_size # Number of samples per buffer
        self.callback = callback # Callback function to process each buffer in a ping pong manner
        self._stop = threading.Event() # Event to stop the acquisition thread
        self._thread = None # Thread for acquisition
        # Two circular buffers for double buffering
        self.buffers = [np.zeros(self.N, dtype=np.int16),
                        np.zeros(self.N, dtype=np.int16)] 

    def _acquire_loop(self):
        idx = 0
        while not self._stop.is_set():
            buf = self.buffers[idx] # Select the current buffer
            for i in range(self.N): # Acquire N samples at fs Hz
                buf[i] = self.spi.read_one()
                time.sleep(self.spi.period)
  
            # Start the processing thread in parallel with the acquired buffer
            if self.callback:
                threading.Thread(
                    target=self.callback,
                    args=(buf.copy(),), # Pass a copy of the buffer to avoid
                    daemon=True
                ).start()
            # switch buffer for the next acquisition
            idx ^= 1
        

    def start(self):
        # Start the acquisition thread if not already running
        if self._thread is None or not self._thread.is_alive(): 
            self._stop.clear() 
            self._thread = threading.Thread(target=self._acquire_loop, daemon=True) 
            self._thread.start()

    def stop(self):
        # Stop the acquisition thread
        self._stop.set()
        if self._thread is not None:
            self._thread.join()


