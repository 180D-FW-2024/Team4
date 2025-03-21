# -*- coding: utf-8 -*-
"""mod_berry

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vJxQwEjDT47DKH4V4wgcPE2mshodgzqn
"""

import sys
import time
import math
import IMU
import datetime
import os
import numpy as np
import tflite_runtime.interpreter as tflite
from smbus2 import SMBus

# Load TFLite model and allocate tensors
interpreter = tflite.Interpreter(model_path="fall_detection_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly

# Sensitivity scale factors (based on datasheet)
ACC_SCALE = 0.061 * 0.00981  # mg/LSB to m/s²
GYRO_SCALE = 8.75 * 0.0000174533  # mdps/LSB to rad/s
MAG_SCALE = 0.08 * 0.1  # mGauss/LSB to μT

a = datetime.datetime.now()

IMU.detectIMU()     #Detect if BerryIMU is connected.
if(IMU.BerryIMUversion == 99):
    print(" No BerryIMU found... exiting ")
    sys.exit()
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass


while True:

    #Read the accelerometer,gyroscope and magnetometer values (RAW)
    ACCx = IMU.readACCx() * ACC_SCALE
    ACCy = IMU.readACCy() * ACC_SCALE
    ACCz = IMU.readACCz() * ACC_SCALE
    GYRx = IMU.readGYRx() * GYRO_SCALE
    GYRy = IMU.readGYRy() * GYRO_SCALE
    GYRz = IMU.readGYRz() * GYRO_SCALE
    MAGx = IMU.readMAGx() * MAG_SCALE
    MAGy = IMU.readMAGy() * MAG_SCALE
    MAGz = IMU.readMAGz() * MAG_SCALE

# Combine data into a single array for the model

    input_data = np.array(ACCx+ACCy+ACCz + GYRx+GYRy+GYRz + MAGx+MAGy+MAGz, dtype=np.float32)

        # Ensure input matches the model's input shape
    input_data = np.expand_dims(input_data, axis=0)  # Shape (1, 9) if model expects 9 features

        # Normalize or scale input if required by your model
        # (Uncomment below line if your model needs normalization)
        # input_data = input_data / np.max(np.abs(input_data), axis=1, keepdims=True)

        # Make prediction
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    print("Inference result:", output_data)

        # Interpret the model's output (classification with 3 possible classes)
        # Assuming the output is a vector of probabilities: [ADLs, Falls, Near Falls]
    predicted_class = np.argmax(output_data)  # Get the index of the highest probability

        # Output "Fall detected!" only if predicted class is 1 (Fall)
    if predicted_class == 1:
        print("Fall detected!")


    #slow program down a bit, makes the output more readable
    time.sleep(0.03)

