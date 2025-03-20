# MAIN SERVER RASPBERRY PI

## Overview
This subfolder contains the codes run in the "Main Server Raspberry Pi" node in the NightWatcher system, a sleep-walking monitoring solution. It handles video processing, playing audio alarms, Telegram communication, UDP communications, and most importantly managing the entire Night Watcher system.
It handles the UDP communication transmissions for real-time video data, fall detection data, step counting data, video & activation mechanism of the mobile rover unit.

## Key Components
1. Camera Output Processing and Data Handling (camera.py)
2. Telegram Bot Integration (telegram_bot.py)
3. Fall Detection UDP Data Receiver (fall_detection_receiver.py)
4. Step Counter UDP Data Receiver (stepcounter_data.py)
5. Speech Recognition Boolean UDP Data Receiver (speech_recognition_data.py)
6. UDP Video Data from Rover unit Receiver (video_rover_receiver.py)
7. System Manager (main.py)

## Features
- Real-time person detection using YOLOv8
- Low-light enhancement with VLight algorithm
- Fall detection with emergency alerts
- Step counting analytic
- Voice activation system
- Mobile rover camera integration
- Telegram bot for remote monitoring and control

## Dependencies
- OpenCV
- Ultralytics YOLO
- PhyCV
- NumPy
- Requests

## Usage
Run `python main.py` to start the NightWatcher system.

## Code Origin and Design Decisions
- The code is based on previous project experience outside of this class.
- Libraries used are familiar to the developer from previous experiences.
- The system is designed with a strong object-oriented approach for modularity and maintainability.
- The architecture follows the initial design closely to maintain a clear and organized directory structure.

## Known Issues
- The system relies heavily on a stable internet connection, particularly for Telegram integration.
- Potential instability if internet connectivity is poor or inconsistent; for instance, unstable LTE hotspot from phone can cause errors in contrast to stable 5G Wi-Fi homen network.

## Future Improvements
- Develop a more robust alert system that doesn't rely solely on internet-dependent platforms like Telegram.
- Explore local UDP or Tailscale UDP connections for improved reliability in alerting instead of relying on Telegram API system.

## Notes
This subfolder is part of the larger NightWatcher system, focusing on the main server components running on a Raspberry Pi. It interfaces with other subsystems to provide comprehensive sleep-walking monitoring and alerts.
