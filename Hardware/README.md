# HDL Coder ECG Filter IP – Project Files

This repository includes the core files used to design and generate an FPGA IP core for ECG signal filtering using MATLAB HDL Coder.


## 1. File Descriptions

### 1.1. `pipeline.mat`

This file contains the complete Matlab model representing the ECG filtering pipeline. It is configured for compatibility with HDL Coder and can be used to generate a custom IP core.

The model includes all processing stages required for basic ECG filtering and is optimized for real-time operation and resource-efficient synthesis on FPGAs.

### 2.2. `QuantizedSOS.mat`

This file includes the quantized coefficients of all IIR filters used in the pipeline, represented in Second-Order Sections (SOS) format.

These coefficients are:

- Quantized for fixed-point hardware implementation.
- Stable and verified for HDL Coder compatibility.
- Meant only for the IIR sections; FIR filters (if present) are not included in this file.


This setup supports rapid deployment of ECG filter chains into hardware for embedded signal processing.

### 2.3. `pipeline_ipcore.zip`

This archive contains the fully generated and manually optimized HDL IP core based on the `pipeline.mat` model. It includes:

- Synthesizable VHDL/Verilog source code.
- IP metadata and constraints.
- Scripts and files for integration into FPGA design environments.

The IP core has been reviewed and fine-tuned for our application.
