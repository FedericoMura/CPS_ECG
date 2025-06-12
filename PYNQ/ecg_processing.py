from pynq import MMIO, allocate
import numpy as np
import scipy.signal as signal
import time

class ECGProcessor:
    IP_BASE = 0x43C00000
    IP_SPAN = 0x1000

    def __init__(self, overlay, dma_name='axi_dma_0', ip_name='pipeline_ipcore_0',
                 window_size=200, fs=200):
        self.fs = fs # Sampling frequency
        self.window = window_size # Size of the processing window
        dma = getattr(overlay, dma_name) # Initialize the DMA controller
        self.dma_send = dma.sendchannel 
        self.dma_recv = dma.recvchannel
        
        length = 0x1000 # Length of the MMIO region
        mmio = MMIO(self.IP_BASE, length) # Create MMIO object for the IP core
        mmio.write(0x8, self.window) # Set the window size in the IP core
        
        self.n_windows = 60 # Number of windows to keep track of peaks
        self.all_peaks = [[] for _ in range(self.n_windows)] 
        self.last_idx  = -100
        self.last_peak_val = -100
        self._in_buf  = allocate((self.window,), dtype=np.int32) # Input buffer 
        self._out_buf = allocate((self.window,), dtype=np.int32) # Output buffer (processed data)
        self.SIG_I_LEV=0
        self.NOISE_I_LEV=0
        self.SIG_PB_LEV   =  0
        self.NOISE_PB_LEV = 0
        self.init_flag=1
        self.overlap_window_pb = np.zeros((50), dtype=np.int16)
        self.ecg_int= np.zeros((0), dtype=np.int16)
        self.ecg_pb= np.zeros((0), dtype=np.int16)
        self.global_indexes = np.zeros((0), dtype=np.int32)
        self.global_indexes_pb=np.zeros((0), dtype=np.int32)
        self.global_index = 0
        self.init_seg_int = np.zeros((0), dtype=np.int32)
        self.init_seg_pb= np.zeros((0), dtype=np.int32)
                

    def _init_thresholds(self, signal16, signal_pb):
        if self.init_flag!=1:
                self.init_seg_int = signal16 
                self.init_seg_pb= signal_pb
                
        if self.init_flag==1:
            self.init_seg_int = np.concatenate((self.init_seg_int, signal16))
            self.SIG_I_LEV   =  np.max(self.init_seg_int)
            self.NOISE_I_LEV = np.mean(self.init_seg_int)
            self.THR_I_1   = self.NOISE_I_LEV + 0.25*(self.SIG_I_LEV - self.NOISE_I_LEV)
            self.THR_I_2 = 0.5*self.THR_I_1

            self.init_seg_pb = np.concatenate((self.init_seg_pb, signal_pb))
            self.SIG_PB_LEV   =  np.max(self.init_seg_pb)
            self.NOISE_PB_LEV = np.mean(self.init_seg_pb)
            self.THR_PB_1   = self.NOISE_PB_LEV + 0.25*(self.SIG_PB_LEV - self.NOISE_PB_LEV)
            self.THR_PB_2 = 0.5*self.THR_PB_1
            self.init_seg_int=None
            self.init_seg_pb=None
        
        self.init_flag=self.init_flag-1

    
    def filter_hw(self, raw_samples):
        """
        raw_samples: np.array of int32, length == window
        Returns np.array int32 filtered by the FPGA
        """
        self._in_buf[:] = raw_samples # copy the input samples to the input buffer
        self.dma_send.transfer(self._in_buf) # send the input buffer to the FPGA
        while not self.dma_send.idle: # wait for the transfer to complete
            time.sleep(0.0001)
        self.dma_recv.transfer(self._out_buf) # receive the output buffer from the FPGA
        while not self.dma_recv.idle:
            time.sleep(0.0001)
        return self._out_buf.copy() # copy the output buffer to a new array

    def detect_peaks_adaptive(self, signal16, signal_pb, min_dist_s=0.25):
        """
        signal16: np.array of int16 (filtered output, QRS enhanced)
        signal_pb: np.array of int16 (band-pass output)
        min_dist_s: minimum distance between R-peaks (in seconds)
        """
        if self.init_flag > 0:
            self._init_thresholds(signal16, signal_pb)
            return None

        fs = self.fs
        min_dist = int(min_dist_s * fs)
        peaks, _ = signal.find_peaks(signal16, distance=min_dist)
        window_peaks = []
        self.ecg_int = np.concatenate((self.ecg_int, signal16))
        self.ecg_pb = np.concatenate((self.ecg_pb, signal_pb))
        for p in peaks:
            val =signal16[p] 
            if self._is_noise(val):
                self._update_noise_level(val)
            else:
                if not self._is_far_enough(p, min_dist):
                    if val > self.last_peak_val:
                        self._replace_last_peak()
                self._update_signal_level(val)
                window_peaks.append(p)
                self.last_peak_val = val
                self.last_idx = p

            self._update_thresholds()

        self._update_peak_history(window_peaks)
        self.global_indexes = np.concatenate((self.global_indexes, np.array(window_peaks) + self.global_index * self.window))
        self.global_index += 1
        return self.all_peaks, self.ecg_int, self.ecg_pb, self.global_indexes
    

    def _is_noise(self, val):
        return val < self.THR_I_1

    def _update_noise_level(self, val):
        self.NOISE_I_LEV = 0.125 * val + 0.875 * self.NOISE_I_LEV

    def _update_signal_level(self, val):
        self.SIG_I_LEV = 0.125 * val + 0.875 * self.SIG_I_LEV

    def _update_thresholds(self):
        self.THR_I_1 = self.NOISE_I_LEV + 0.25 * (self.SIG_I_LEV - self.NOISE_I_LEV)
        self.THR_I_2 = 0.5 * self.THR_I_1  

    def _is_far_enough(self, current_idx, min_dist):
        return (self.window + current_idx) - self.last_idx >= min_dist

    def _replace_last_peak(self):
        if self.all_peaks[-1]:
            self.all_peaks[-1] = self.all_peaks[-1][:-1]

    def _update_peak_history(self, window_peaks):
        self.all_peaks.append(window_peaks)
        actual=self.all_peaks.pop(0)

    def compute_bpm_recent_average(self, n=5):
        valid_windows = self.all_peaks[-n:] if len(self.all_peaks) >= n else self.all_peaks
        total_peaks = sum(len(peaks) for peaks in valid_windows)
        total_duration = len(valid_windows) * (self.window / self.fs)

        if total_duration <= 0:
            return 0.0
        return total_peaks / total_duration * 60.0
    


    def detect_peaks_adaptive2(self, signal16, signal_pb, min_dist_s=0.25):
        """
        signal16: np.array of int16 (filtered output, QRS enhanced)
        signal_pb: np.array of int16 (band-pass output)
        min_dist_s: minimum distance between R-peaks (in seconds)
        """
        if self.init_flag > 0:
            self._init_thresholds(signal16, signal_pb)
            self.overlap_window_pb=signal_pb[int(-min_dist_s*self.fs):]
            return

        fs = self.fs
        min_dist = int(min_dist_s * fs)
        peaks, _ = signal.find_peaks(signal16, distance=min_dist)
        window_peaks = []
        self.ecg_int = np.concatenate((self.ecg_int, signal16))
        self.ecg_pb = np.concatenate((self.ecg_pb, signal_pb))
        signal_pb=np.concatenate((self.overlap_window_pb, signal_pb))
        for p in peaks:
            val_int = signal16[p]
            # Window centered on p in signal_pb
            w = 40  # half window, so total 41 samples
            left  = max(0, len(self.overlap_window_pb) + p - w)
            right = len(self.overlap_window_pb) + p
            window_pb = signal_pb[left:right]
            
            local_idx_pb = np.argmax(window_pb)         # local index in the window
            val_pb_peak = window_pb[local_idx_pb]       # maximum value

            if self._is_noise(val_int) or val_pb_peak < self.THR_PB_1:
                # if the integrated peak is below threshold, or there is no support in the band-pass
                self._update_noise_level(val_int)
                self.NOISE_PB_LEV = 0.125 * val_pb_peak + 0.875 * self.NOISE_PB_LEV
            else:
                # passes both conditions
                if not self._is_far_enough(p, min_dist):
                    if val_int > self.last_peak_val:
                        self._replace_last_peak()
                self._update_signal_level(val_int)
                self.SIG_PB_LEV = 0.125 * val_pb_peak + 0.875 * self.SIG_PB_LEV
                window_peaks.append(p)
                self.last_peak_val = val_int
                self.last_idx = p
                abs_idx_pb = left + local_idx_pb + self.window*self.global_index - len(self.overlap_window_pb )
                self.global_indexes_pb=np.append(self.global_indexes_pb, abs_idx_pb)
            self._update_thresholds()
            self.THR_PB_1 = self.NOISE_PB_LEV + 0.25 * (self.SIG_PB_LEV - self.NOISE_PB_LEV)
            self.THR_PB_2 = 0.5 * self.THR_PB_1
        
        self._update_peak_history(window_peaks)
        self.global_indexes = np.concatenate((self.global_indexes, np.array(window_peaks) + self.global_index * self.window))
        self.global_index += 1
        self.overlap_window_pb=signal_pb[int(-min_dist_s*self.fs):]
        return
