# How to Run the Autonomous Rover System with Object Detection

This folder contains all the necessary code for the Rover to be able to actviate the object detection and follow the subject.
## Install Dependencies
Run the following command to install the required Python libraries:
```bash
pip install opencv-python numpy pyserial
```

## Understanding the `Object_Detection_Files` Folder
The **`Object_Detection_Files`** folder is essential for object detection using the **SSD MobileNet** model in OpenCV. It includes:
- **`coco.names`** → List of class labels for object detection (e.g., "person", "car").
- **`frozen_inference_graph.pb`** → Pre-trained TensorFlow model for object detection.
- **`ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt`** → Configuration file for the SSD MobileNet model.

---
## Setting Up the Rover System
Create a folder, for example, **`Rover Activation`**, and include the following scripts inside it:
- `cam_CPU.py`
- `receiver.py`
- `motor.py`
- `main.py`
- `Object_Detection_Files/` *(with the required model files inside)*

## Starting the Rover System
Assuming `main.py` is the activation script within the **Rover Activation** folder, run the following command:
```bash
sudo python main.py
```

## Code Origin & Design

### 1. Code Origin

The object detection system is built on:
- **OpenCV’s DNN module** using the **SSD MobileNet v3 COCO model**.
- The model files were sourced from **TensorFlow’s Model Zoo** and adapted for CPU inference on Raspberry Pi.
- Motor control uses **PySerial** for communication with a serial-connected motor driver.

### 2. Design Overview

- When activated, the system uses a **Raspberry Pi Camera** to capture live frames.
- These frames are passed through the SSD object detection model to identify a person.
- The algorithm calculates:
  - **Size of the bounding box** to determine distance (larger = closer).
  - **Horizontal offset** to determine direction (left or right of center).
- A differential drive system adjusts the speed of the left and right wheels to follow the detected person.
- **Detection Thresholds**:
  - Bounding boxes below a confidence threshold (e.g., 0.5) are ignored.
  - Small movements are filtered out to prevent jittery or erratic motion.
- **Collision Prevention**:
  - The bounding box size is clamped to stop the rover before crashing into the user.
  - Turns are rate-limited to keep motion smooth and avoid overcorrection.
- **UDP Control Interface**:
  - The rover waits for a signal from the **Main Processor Pi** before it begins operating.
  - This prevents false triggering and ensures synchronized operation with the rest of the Nightwatcher system.
 

## Known Issues
There is a delay in sending frames to the main server if the internect connection is not stable. It will still work but may send the position at a certain lag.

## Future Improvements
Have a more robust protocol where frames can be sent in smaller packet sizes or quality tradeoff in order to ensure frames are sent in time to the main server for real-time monitoring.



