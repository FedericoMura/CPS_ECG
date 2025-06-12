# ECG Real-time Monitoring System on Pynq Z1

This project implements a real-time Electrocardiogram (ECG) and Heart Rate (HR) monitoring system using a Pynq Z1 board, an STM32 Nucleo-64 board, and an AD8232 ECG sensor. The primary goal is to acquire ECG signals, process noise, identify R-peaks, and calculate heart rate.

## 1. Introduction

This system is designed to acquire ECG data from a subject, apply advanced filtering and analysis techniques, and provide real-time information about heart rate and its variability. The Pan & Tompkins algorithm is utilized for R-peak detection, which are subsequently used for heart rate calculations. The system has been validated using publicly available patient data and has demonstrated good efficacy.

## 2. Hardware Components Required

To use this project, you will need the following components:

* Pynq Z1 Board: The main platform for signal processing.
* STM32 Nucleo-64 Board (with STM32 microcontroller): Responsible for data acquisition from the ECG sensor.
* AD8232 ECG Sensor: The sensor for electrocardiographic signal acquisition.
* Jumper Wires: For connecting the Pynq to the Nucleo and the Nucleo to the AD8232 sensor.
* MicroSD Card: Pre-loaded with the Pynq OS image.
* USB mini-B cable: For connecting the Nucleo to your computer for programming.

## 3. Hardware Setup

### 3.1. STM32 Nucleo-64 Pin Mapping

The following pins on the STM32 Nucleo-64 board are used:

* ECG Analog Input (AD8232 OUT) → `PA0` (`ADC_IN`)
* SPI NSS (Slave Select) → `PA4`
* SPI SCK (Clock) → `PA5`
* SPI MISO (Master In Slave Out) → `PA6`
* SPI MOSI (Master Out Slave In) → `PA7`

Ensure that the ECG signal from the AD8232 sensor is connected to pin `PA0`, and that the SPI connections between the Nucleo and Pynq match the pin assignments above.

Follow these steps to connect the hardware components:

1. Connecting AD8232 Sensor to STM32 Nucleo-64:
   * Connect the analog output of the AD8232 sensor to an analog input pin on the STM32 Nucleo-64.
   * Connect the power pins (VCC and GND) of the AD8232 sensor to the corresponding power pins on the STM32 Nucleo-64.
   * Ensure the AD8232 sensor electrodes are properly connected for ECG acquisition (e.g., RA, LA, RL).

2. Connecting STM32 Nucleo-64 to Pynq Z1 (via SPI):
   * Identify the SPI pins (MOSI, MISO, SCLK, NSS) on your STM32 Nucleo-64 board.
   * Identify the corresponding SPI pins on the Pynq Z1 board.
   * Connect the Nucleo's SPI pins to the Pynq:
     * Nucleo MISO → Pynq MISO
     * Nucleo MOSI → Pynq MOSI
     * Nucleo SCLK → Pynq SCLK
     * Nucleo NSS (Slave Select) → Pynq NSS
   * Ensure that the grounds (GND) of both boards are connected.

Note: The Pynq will act as the SPI master, and the Nucleo as the slave. Data transfers will be serial 16-bit. The sensor sampling rate is 200 Hz.

## 4. Software Setup

The project involves firmware for the Nucleo-64 and a Jupyter Notebook for the Pynq Z1.

### 4.1. Nucleo-64 Firmware Upload and Project Configuration

To run the firmware on the STM32 Nucleo-64 board, you must import and build the project provided as a `.ioc` file (named `ECG.ioc`) using STM32CubeIDE.

Steps:

1. Install STM32CubeIDE from the official STMicroelectronics website:  
   https://www.st.com/en/development-tools/stm32cubeide.html  
   You must create and log in with a free STMicroelectronics account to download the software and board support files.

2. Open STM32CubeIDE.

3. Go to `File → Open Projects from File System…`, browse to the folder containing the `ECG.ioc` file, and import the project into your workspace.

4. Click `GENERATE CODE` to initialize the project structure.
   * This step will create the full folder structure under `/Core`, including `main.c`.

5. Replace the generated file `Core/Src/main.c` with the provided version from this repository, which contains the logic for ECG acquisition and SPI communication.

   If you do not have the ECG sensor available, you can still simulate the signal:
   - Download the file `ecg_data.h` and place it in the `Core/Inc` directory.
   - Use the file `main_noadc.c` (also provided) and rename it to `main.c`.
   - Replace the generated `Core/Src/main.c` with this renamed file.
   This version of the firmware will transmit pre-recorded ECG data instead of acquiring it from the sensor.


6. Build the project by clicking the hammer icon.

7. Connect the Nucleo board to your computer using a USB mini-B cable.

8. Flash the firmware:
   * Click the green debug arrow or go to `Run → Debug As → STM32 Cortex-M C/C++ Application`.

9. Once flashed, the Nucleo will:
    * Continuously acquire analog ECG data from the AD8232 sensor.
    * Sample the signal at 200 Hz and transmit 16-bit words via SPI to the Pynq Z1.

### 4.2. MicroSD Card Preparation (for Pynq)

* Ensure your MicroSD card contains the Pynq operating system image.
* Insert the MicroSD card into the dedicated slot on the Pynq Z1.

### 4.3. Upload Pynq Overlay Files

* Before running the Jupyter Notebook, upload the hardware overlay files to your Pynq board. These files (`ecg_hw.bit` and `ecg_hw.hwh`) define the custom hardware accelerators (e.g., filters) on the FPGA.
* Transfer these files to the Pynq board using SCP, SFTP, or by copying them directly to the MicroSD card. Place them in the same directory as the Jupyter Notebook.

### 4.4. Accessing Jupyter Notebook

* Connect the Pynq Z1 to your network (Ethernet or configured Wi-Fi).
* Power on the board.
* Open a web browser and go to the Pynq Z1's IP address (typically 192.168.2.1 if connected directly).
* Log in to the Jupyter Notebook interface.

### 4.5. Upload Project Notebook

* Upload the Jupyter Notebook file (`ecg_Notebook.ipynb`) containing the project’s Python script to the working directory on the Pynq board.

## 5. Running the Project

1. Open the Jupyter Notebook file uploaded to the Pynq.
2. Execute all cells in order. The script will:
   * Load the custom hardware overlay (.bit and .hwh files).
   * Configure SPI communication with the Nucleo.
   * Manage DMA transfers (200-word buffer, 32-bit words).
   * Invoke hardware IP for ECG filtering.
   * Run the Pan & Tompkins algorithm for R-peak detection.
   * Calculate heart rate based on R-R intervals.

## 6. Output and Interpretation

Once running, the following outputs will be observed:

* Heart Rate (LED): An onboard LED will flash based on the detected heart rate.
* Heartbeat Graph: A real-time ECG graph showing detected R-peaks.

The system has been tested with noisy and varied heart rate data and has shown good performance.

## 7. Troubleshooting

* No data or incorrect data:
  * Check SPI wiring, power connections, and sensor orientation.
  * Ensure the Nucleo firmware is flashed and running correctly.
  * Confirm that SPI settings in the Jupyter script match the firmware.

* Pynq inaccessible:
  * Ensure power is on and the MicroSD is correctly inserted.
  * Check network configuration and IP address.

* Jupyter Notebook errors:
  * Ensure overlay files (.bit and .hwh) are correctly placed.
  * Run all cells sequentially.
  * Review output logs and messages for additional hints.
