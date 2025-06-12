1.1. Creating the STM32 Nucleo-64 Project with STM32CubeIDE

To run the firmware on the STM32 Nucleo-64 board, you must import and build the project provided as a `.ioc` file (named `ECG.ioc`) using STM32CubeIDE.

### Steps:

1. Install **STM32CubeIDE** from the official STMicroelectronics website:  
   https://www.st.com/en/development-tools/stm32cubeide.html  
   > ⚠️ You will need to create and log in with a free STMicroelectronics account to download the software and board files.

2. Open **STM32CubeIDE**.

3. Go to `File → Open Projects from File System…`, browse to the folder containing the `ECG.ioc` file, and import the project into your workspace.

4. If STM32CubeIDE does not recognize your board configuration:
   - Click `GENERATE CODE` to initialize the project structure.
   - This step will automatically create the necessary folder tree under `/Core`, including `main.c`.

5. Once code generation is complete:
   - Replace the newly generated file `Core/Src/main.c` with the provided version from this repository (`main.c` customized for ECG acquisition and SPI transfer).

6. Ensure the peripheral configuration is correct:
   - `ADC1` is enabled and connected to the analog input pin where the AD8232 output is wired.
   - `SPI1` (or the selected SPI peripheral) is configured in **Slave Mode**, with 16-bit data size.
   - DMA is enabled for SPI reception and/or ADC as needed.

7. Build the project by clicking the **hammer icon**.

8. Connect the Nucleo-64 to your computer using a USB mini-B cable.

9. Flash the firmware to the board:
   - Click the green debug arrow or go to `Run → Debug As → STM32 Cortex-M C/C++ Application`.

10. Once flashed, the Nucleo will:
    - Continuously acquire analog ECG data from the AD8232 sensor.
    - Sample the signal at 200 Hz and transmit 16-bit words via SPI to the Pynq Z1 board.

> 💡 The firmware is editable. You can add preprocessing filters, R-peak marking, or custom logic if needed.
