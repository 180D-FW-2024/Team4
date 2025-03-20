# Team4

This is a Sleepwalker detection project with its intended usage to be a monitoring Internet of Things Sytem (IoT). This has multiples components that we will list below and how to run. So far there are 3 Agents with various codes to be run for the Nightwatcher to be effectively working. 

# Installation and Setup

## Prerequisites
Ensure you have **Python 3.x** installed on your system.


## How to run the Speech Processor 
## Install Dependencies
Run the following command to install the required Python libraries:
```bash
pip install speechrecognition requests edge-tts langchain langchain_groq groq pydantic
```
### Running the Speech Processor
```bash
python speechpi.py
```

### How to run the Autonmous Rover system with Object Detection
## Install Dependencies
Run the following command to instal the required Python libraries: 
```bash
pip install opencv-python numpy pyserial
```
## Installing and Understanding the 'Object_Detection_Files' Folder
- `coco.names` is a list of class labels for object detection (e.g., "person", "car") to help identify what the Rover is looking at.
- `frozen_inference_graph.pb` is a pre-trained TensorFlow model for object detection.
- `ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt` is the  Configuration file for the SSD MobileNet model.

## Create a Folder with all files and dependencies 
Within a folder for example called "Rover Activation" include the following scripts in the folder. 
- 'cam_CPU.py'
- 'receiver.py'
- 'motor.py'
- 'main.py'
- 'Object_Detection_Files'
  
## Starting up the Rover: assuming main is the activation code within Rover Folder 
```bash
sudo python main.py 
```
