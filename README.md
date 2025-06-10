# ECG and HRV Real-time Monitoring System on Pynq Z1

This project implements a real-time Electrocardiogram (ECG) and Heart Rate Variability (HRV) monitoring system using a Pynq Z1 board, an STM32 Nucleo-64 board, and an AD8232 ECG sensor. The primary goal is to acquire ECG signals, process noise, identify R-peaks, and calculate heart rate and HRV.

## 1. Introduction

This system is designed to acquire ECG data from a subject, apply advanced filtering and analysis techniques, and provide real-time information about heart rate and its variability. The Pan & Tompkins algorithm  is utilized for R-peak detection, which are subsequently used for heart rate and HRV calculations. The system has been validated using publicly available patient data and has demonstrated good efficacy.

## 2. Hardware Components Required

To use this project, you will need the following components:

* **Pynq Z1 Board:** The main platform for signal processing.
* **STM32 Nucleo-64 Board (with STM32 microcontroller):** Responsible for data acquisition from the ECG sensor.
* **AD8232 ECG Sensor:** The sensor for electrocardiographic signal acquisition.
* **Jumper Wires:** For connecting the Pynq to the Nucleo and the Nucleo to the AD8232 sensor.
* **MicroSD Card:** Pre-loaded with the Pynq OS image.

## 3. Hardware Setup

Follow these steps to connect the hardware components:

1.  **Connecting AD8232 Sensor to STM32 Nucleo-64:**
    * Connect the analog output of the AD8232 sensor to an analog input pin on the STM32 Nucleo-64.
    * Connect the power pins (VCC and GND) of the AD8232 sensor to the corresponding power pins on the STM32 Nucleo-64.
    * Ensure the AD8232 sensor electrodes are properly connected for ECG acquisition (e.g., RA, LA, RL).

2.  **Connecting STM32 Nucleo-64 to Pynq Z1 (via SPI):**
    * Identify the SPI pins (MOSI, MISO, SCLK, NSS) on your STM32 Nucleo-64 board.
    * Identify the corresponding SPI pins on the Pynq Z1 board.
    * Connect the Nucleo's SPI pins to the Pynq:
        * `Nucleo MOSI` $\rightarrow$ `Pynq MISO`
        * `Nucleo MISO` $\rightarrow$ `Pynq MOSI`
        * `Nucleo SCLK` $\rightarrow$ `Pynq SCLK`
        * `Nucleo NSS` (Slave Select) $\rightarrow$ `Pynq GPIO` (any GPIO pin configured as chip select)
    * Ensure that the grounds (GND) of both boards are connected.

    *Note:* The Pynq will act as the SPI *master*, and the Nucleo as the *slave*. Data transfers will be serial 16-bit. The sensor sampling rate is 200 Hz.

## 4. Software Setup

The project utilizes the Jupyter Notebook environment on the Pynq Z1 board.

1.  **MicroSD Card Preparation:**
    * Ensure your MicroSD card contains the Pynq operating system image.
    * Insert the MicroSD card into the dedicated slot on the Pynq Z1.

2.  **Accessing Jupyter Notebook:**
    * Connect the Pynq Z1 to your network (via Ethernet or Wi-Fi, if configured).
    * Power on the Pynq Z1.
    * Open a web browser on your computer and navigate to the IP address of your Pynq Z1 (usually `192.168.2.1` if connected directly to your computer, otherwise check the IP address assigned by your network).
    * Log in to the Jupyter Notebook interface.

3.  **Project Upload:**
    * Upload your Jupyter Notebook file (`.ipynb`) containing the project's Python script to the Jupyter working directory on the Pynq.

## 5. Running the Project

1.  **Open the Jupyter Notebook:** Once uploaded, open your project's Jupyter Notebook file.
2.  **Execute the Python Script:** Within the notebook, execute the cells in sequence. The Python script will handle:
    * Configuring SPI communication with the Nucleo.
    * Managing data transfers via DMA (200-word buffer, 32-bit words).
    * Invoking the hardware IP for filters (pre-configured) for ECG signal processing.
    * [cite_start]Implementing the Pan & Tompkins algorithm  for R-peak detection.
    * Calculating Heart Rate and Heart Rate Variability (HRV) based on R-R intervals.

## 6. Output and Interpretation

Once the script is running, you will observe the following outputs:

* **Heart Rate (LED):** An LED on the Pynq Z1 board will flash according to the detected heart rate.
* **Heartbeat Graph:** A real-time graph of the ECG signal will be displayed, showing the R-peaks identified by the Pan & Tompkins algorithm.
* **HRV Values:** Calculated Heart Rate Variability (HRV) values will be displayed. These values can be interpreted to assess the state of the autonomic nervous system.

[cite_start]The algorithm has been validated with data containing significant noise and various heart rates, demonstrating its efficacy.

## 7. Troubleshooting

* **No data or incorrect data:**
    * Check all hardware connections (SPI, sensor, power).
    * Verify that the Nucleo is indeed acquiring and sending data correctly.
    * Ensure that the SPI configuration in the Python script precisely matches the hardware configuration.
* **Pynq inaccessible:**
    * Verify that the Pynq is powered on and the MicroSD card is properly inserted.
    * Check your network connection and the Pynq's IP address.
* **Error in Jupyter script:**
    * Assure you have executed all cells in order.
    * Check for any error messages in the terminal or notebook output.
