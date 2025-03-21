## Fall Detection & Step Counter

## Overview
This subfolder contains the codes run for the IMU features of the "Wearable Device RPi" node in the NightWatcher system. The `mainimu.py` script is the source code and is the Nightwatcher's fall detection and step counter algorithms combined into one runnable code.
It communicates data via UDP communication transmissions for real-time falling detection and step counting. 

## Key Components
1. Libraries 
2. Source Code (main.py)

## Features
- Real-time falling-detection
- Real-time step counting

## Dependencies
- IMU (Ozzmaker's Github)
- NumPy
- JavaScript Object Notation
- Socket

## Usage
Run `mainimu.py` (saved alongside the other files in this folder) to start the IMU features of the Nightwatcher system.
```bash
python mainimu.py
```

## Code Origin and Design Decisions
- The .py scripts alongside the mainimu.py are from Ozzmaker's BerryIMU github, where it provides a library for reading the angles from the accelerometer, gyroscope, and magnetometer on a BerryIMU connected to a Raspberry Pi.
- Both the fall detection and step counting depends on alogrithmic calculations to maximize efficiency while simplyfing the processing power, rather than using a learned model
- The architecture is simplified from the original idea of using a learned model to account for the latency in other aspects of the system.

## Known Issues
- The script relies heavily on a stable internet connection, since it is using UDP connection to send data to the main Raspberry Pi

## Future Improvements
- Develop a more robust communications system that doesn't rely solely on internet-dependent connections
- Explore machine learned models to handle fall detection optimally on a Raspberry Pi 4

## Notes
This subfolder is part of the larger NightWatcher system, focusing on the features provided by an IMU connected on a Raspberry Pi. It interfaces with the main Raspberry Pi to provide real-time sleep-walking monitoring.
