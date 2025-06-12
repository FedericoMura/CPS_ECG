import threading, time
from pynq import Overlay
from pynq import MMIO

class ECGBlinker:
    def __init__(self, overlay):
        self.leds   = MMIO (0x41200000, 0x1000) # Base address of the LED controller
        self._bpm   = 60.0 # Default beats per minute
        self._stop  = threading.Event() # Event to stop the blinking thread
        self._thread= None

    def _get_color(self, bpm):
        if 40 <= bpm <= 100: # Normal range
            return 0b010
        if bpm <= 0:        # No heartbeat detected
            return 0b000
        if 100 < bpm <= 170: # Elevated heart rate
            return 0b110
        return 0b100

    def _blink_loop(self):
        self._stop.clear() 
        while not self._stop.is_set(): # Loop until stopped
            bpm = self._bpm 
            if bpm>0: # Calculate half period based on bpm
                half = 30.0/bpm  # Convert bpm to seconds per beat
            else:
                half = 1.0 
            c   = self._get_color(bpm) # Get the color based on bpm
            self.leds.write(0x0, c) # Set the LED color
            time.sleep(half) # Wait for half the period
            self.leds.write(0x0, 0b000) # Turn off the LED
            time.sleep(half) 

    def start(self):
        if not self._thread or not self._thread.is_alive(): # Start a new thread if not already running
            self.leds.write(0x4, 0x0) 
            self._thread = threading.Thread(target=self._blink_loop, daemon=True)
            self._thread.start()
            

    def stop(self):
        self._stop.set() # Signal the thread to stop
        if self._thread:
            self._thread.join()

    def update_bpm(self, bpm):
        self._bpm = bpm # Update the beats per minute for the blinking logic
        
