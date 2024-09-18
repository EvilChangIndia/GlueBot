# GlueBot- An automated gluing robot!

## Description
This is my Microphone Assembly Robot project! This repository contains the code, hardware specifications, and assembly instructions for an advanced robotic system designed to clamp a microphone and apply silicone glue around it using a ZY Cartesian robot. This innovative solution enhances efficiency and precision in the microphone assembly process, ensuring high-quality results every time. This was designed for a specific use case during mz internship, but can be ported for your application.
The project follows a state machine approach.

## Table of Contents
- Hardware Setup
- Installation
- Usage
- Contributing

## Hardware Setup
- Configuration ZY linear cartesian robot with dispenser at TCP. Additionallz mic clamped along X and rotated about the same axis.
- Controller : Esp32 NodeMCU (espressif)
- Firmware : Grbl_Esp32 cnc firmware( https://github.com/bdring/Grbl_Esp32 )
- UI : Rpi3B + 7inch Display. Footpedal
- Glue Dispenser : Loctite dispenser with pedal
- Linear axes ( x 2) : Nema 17, nema 23 + linear drives (Igus)
- Rotary Axis : Harmonic drive + Nema 17  (Igus)
- Clamping : Pneumatic actuator (Igus) + relays

## Installation
1. Clone this repository into your PC:
   ```
   git clone https://github.com/EvilChangIndia/GlueBot.git
   ```
2. Flashing the Esp32 firmware:
   I have used **Grbl_Esp32** cnc firmware by **bdring** for the project. Follow the instruction on their repository to flash the firmware onto your Esp32.
   - Clone the firmware into your PC or download as zip:
     ```
     git clone https://github.com/bdring/Grbl_Esp32.git
     ```
   - **IMPORTANT!!!** : It is important to define our hardware and wiring configuration in the firmware before flashing it onto the Esp.
     This mainly involves two changes:
     - Copy the machine definition file (Esp32/Machine file/GlueBot.h) into the machine folder (Grbl_Esp32/src/Machines) of the firmware.
     - Once you have copied the file, you select it by editing the file "Grbl_Esp32/src/Machine.h" to "#include" your file
   - These steps can be understood in detail by refering to the WiKi inside the firmware repository
     - Repository : https://github.com/bdring/Grbl_Esp32
     - WiKi : https://github.com/bdring/Grbl_Esp32/wiki/Compiling-the-firmware

3. Copy (or download) the contents of **Raspberry Pi** folder into your Raspberry Pi's main folder.


## Usage
To run the program, follow these steps:

1. On RPi terminal, enter:
  ```
  python3 GlueBot/ui/glueBot.py
  ```
2. Control Methods:
- The bot can be controlled using the graphical UI made using GTK
- The foot pedal is used to manually dispense the glue if/when needed. This by-passes the ESP 32.

## **Optional**
   Shell Setup:
   If you want the clampUI.py to start automatically when your Raspberry Pi boots up, you can set up a shell script:
   -  Create a shell script (e.g., start_clamp.sh) with the following content:
      ```
      #!/bin/bash
      python3 /path/to/your/glueBot.py
      ```
   - Make the script executable:
     ```
     chmod +x start_clamp.sh
     ```
   - Add the script to your crontab to run at startup:
     ```
     crontab -e#
     ```
   - Add the following line to the end of the file:
     ```
     @reboot /path/to/your/start_clamp.sh
     ```
## Contributing
We welcome contributions! If you have ideas for improvements or new features, please fork the repository and submit a pull request. For any issues, feel free to open an issue in the GitHub tracker.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

Enjoy using your Gluing Robot!
