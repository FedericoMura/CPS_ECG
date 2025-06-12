# ECG and HRV Real-time Monitoring System on Pynq Z1

This project implements a real-time Electrocardiogram (ECG) and Heart Rate Variability (HRV) monitoring system using a Pynq Z1 board, an STM32 Nucleo-64 board, and an AD8232 ECG sensor. The primary goal is to acquire ECG signals, process noise, identify R-peaks, and calculate heart rate and HRV.

## 1. Introduction

This system is designed to acquire ECG data from a subject, apply advanced filtering and analysis techniques, and provide real-time information about heart rate and its variability. The Pan & Tompkins algorithm is utilized for R-peak detection, which are subsequently used for heart rate and HRV calculations. The system has been validated using publicly available patient data and has demonstrated good efficacy.

## 2. Hardware Components Required

To use this project, you will need the following components:

* **Pynq Z1 Board:** The main platform for signal processing.
* **STM32 Nucleo-64 Board (with STM32 microcontroller):** Responsible for data acquisition from the ECG sensor.
* **AD8232 ECG Sensor:** The sensor for electrocardiographic signal acquisition.
* **Jumper Wires:** For connecting the Pynq to the Nucleo and the Nucleo to the AD8232 sensor.
* **MicroSD Card:** Pre-loaded with the Pynq OS image.
* **USB mini-B cable:** For connecting the Nucleo to your computer for programming.

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

The project involves firmware for the Nucleo-64 and a Jupyter Notebook for the Pynq Z1.

1.  **Nucleo-64 Firmware Upload:**
    * Locate the C firmware file for the STM32 Nucleo-64 in this repository (e.g., `nucleo_firmware.c` or similar).
    * Connect your STM32 Nucleo-64 board to your computer using a USB mini-B cable.
    1.1. **Creating the STM32 Nucleo-64 Project with STM32CubeIDE:**

   To run the firmware on the Nucleo, you must import and build the project provided as a `.ioc` file (named `ECG.ioc`) using STM32CubeIDE.
   
   * **Install STM32CubeIDE** from the official STMicroelectronics website:  
     https://www.st.com/en/development-tools/stm32cubeide.html
   
   * **Open STM32CubeIDE** and import the project:
     * Go to `File → Open Projects from File System…`
     * Browse to the folder containing the `ECG.iop` file.
     * Select and import the project into your workspace.
   
   * **Build the firmware**:
     * Click the hammer icon to compile the project.
     * Ensure that the ADC is configured to sample the ECG signal at 200 Hz.
     * Ensure that the SPI interface is set to **Slave mode** with 16-bit data size and DMA enabled.
   
   * **Flash the firmware to the board**:
     * Connect the Nucleo-64 to your computer using a USB mini-B cable.
     * Click the green debug arrow (`Run → Debug As → STM32 Cortex-M C/C++ Application`) to program the board.
   
   * Once flashed, the Nucleo will:
     * Continuously acquire analog ECG data from the AD8232 sensor.
     * Sample at 200 Hz and transmit 16-bit words via SPI to the Pynq Z1 board.
   
   > *Note:* The firmware source is fully editable.
   
   2.  **MicroSD Card Preparation (for Pynq):**
       * Ensure your MicroSD card contains the Pynq operating system image.
       * Insert the MicroSD card into the dedicated slot on the Pynq Z1.
   
   3.  **Upload Pynq Overlay Files:**
       * Before running the Jupyter Notebook, you need to upload the hardware overlay files to your Pynq board. These files (`.bit` and `.hwh`) define the custom hardware accelerators (like your filters) on the FPGA.
       * Transfer these files from this repository (or your development environment) to the Pynq board. You can typically do this using SCP, SFTP, or by directly copying them to the MicroSD card. Place them in the same directory as your Jupyter Notebook.
   
   4.  **Accessing Jupyter Notebook:**
       * Connect the Pynq Z1 to your network (via Ethernet or Wi-Fi, if configured).
       * Power on the Pynq Z1.
       * Open a web browser on your computer and navigate to the IP address of your Pynq Z1 (usually `192.168.2.1` if connected directly to your computer, otherwise check the IP address assigned by your network).
       * Log in to the Jupyter Notebook interface.
   
   5.  **Project Upload (Jupyter Notebook):**
       * Upload your Jupyter Notebook file (`.ipynb`) containing the project's Python script to the Jupyter working directory on the Pynq.

## 5. Running the Project

1.  **Open the Jupyter Notebook:** Once uploaded, open your project's Jupyter Notebook file.
2.  **Execute the Python Script:** Within the notebook, execute the cells in sequence. The Python script will handle:
    * Loading the custom hardware overlay (using the `.bit` and `.hwh` files).
    * Configuring SPI communication with the Nucleo.
    * Managing data transfers via DMA (200-word buffer, 32-bit words).
    * Invoking the hardware IP for filters (pre-configured) for ECG signal processing.
    * Implementing the Pan & Tompkins algorithm for R-peak detection.
    * Calculating Heart Rate and Heart Rate Variability (HRV) based on R-R intervals.

## 6. Output and Interpretation

Once the script is running, you will observe the following outputs:

* **Heart Rate (LED):** An LED on the Pynq Z1 board will flash according to the detected heart rate.
* **Heartbeat Graph:** A real-time graph of the ECG signal will be displayed, showing the R-peaks identified by the Pan & Tompkins algorithm.
* **HRV Values:** Calculated Heart Rate Variability (HRV) values will be displayed. These values can be interpreted to assess the state of the autonomic nervous system.

The algorithm has been validated with data containing significant noise and various heart rates, demonstrating its efficacy.

## 7. Troubleshooting

* **No data or incorrect data:**
    * Check all hardware connections (SPI, sensor, power).
    * Verify that the Nucleo firmware has been successfully uploaded and is running.
    * Ensure that the Nucleo is indeed acquiring and sending data correctly.
    * Assure that the SPI configuration in the Python script precisely matches the hardware configuration.
* **Pynq inaccessible:**
    * Verify that the Pynq is powered on and the MicroSD card is properly inserted.
    * Check your network connection and the Pynq's IP address.
* **Error in Jupyter script:**
    * Ensure you have uploaded the `.bit` and `.hwh` files to the Pynq and they are in the correct directory.
    * Assure you have executed all cells in order.
    * Check for any error messages in the terminal or notebook output.
