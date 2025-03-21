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
