# Team 4: Sleepwalker Detection System

## Project Overview
This is a **Sleepwalker Detection Project**, designed as a monitoring **Internet of Things (IoT) System**. The system consists of multiple components working together to ensure real-time detection and response. Currently, there are **three agents** with various codes that must be executed for the **Nightwatcher** system to function effectively.

---

# Installation and Setup

## Prerequisites
Ensure you have **Python 3.x** installed on your system.

---

# How to Run the Speech Processor

## Install Dependencies
Run the following command to install the required Python libraries:
```bash
pip install speechrecognition requests edge-tts langchain langchain_groq groq pydantic
```

## Hardware Setup
Ensure that both the **microphone and speaker** are connected to the Raspberry Pi before running the speech processor unit.

## Running the Speech Processor
```bash
python speechpi.py
```

---

# How to Run the Autonomous Rover System with Object Detection

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
