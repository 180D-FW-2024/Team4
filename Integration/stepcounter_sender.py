import socket
import time
import math
import IMU
import datetime
import sys
import json 

# UDP Setup
UDP_IP = "192.168.1.16"  # Receiver's IP (main Raspberry Pi)
UDP_PORT = 5005          # Receiver's port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Step detection variables
previous_magnitude = 0
step_count = 0
threshold = 0.3  # Adjust based on testing
last_step_time = 0
debounce_interval = 0.3  # Minimum time between steps in seconds

# IMU Setup
IMU.detectIMU()  # Detect if BerryIMU is connected
if IMU.BerryIMUversion == 99:
    print("No BerryIMU found... exiting")
    sys.exit()
IMU.initIMU()  # Initialize accelerometer, gyroscope, and compass

def detect_step(ACCx, ACCy, ACCz):
    """
    Detect steps based on the magnitude of the acceleration vector.
    """
    global previous_magnitude, step_count, last_step_time

    # Calculate the magnitude of the acceleration vector
    magnitude = math.sqrt(ACCx**2 + ACCy**2 + ACCz**2)

    # Apply a smoothing function to reduce noise
    smoothed_magnitude = 0.9 * previous_magnitude + 0.1 * magnitude
    current_time = time.time()

    if smoothed_magnitude > threshold and (current_time - last_step_time) > debounce_interval:
        step_count += 1
        last_step_time = current_time
        print(f"Step detected! Total steps: {step_count}")

    previous_magnitude = smoothed_magnitude

while True:
    # Read accelerometer data
    ACCx_raw = IMU.readACCx()
    ACCy_raw = IMU.readACCy()
    ACCz_raw = IMU.readACCz()

    # Normalize the raw data to real-world units (g)
    scale_factor = 16384  # Assuming Â±2g range
    ACCx = ACCx_raw / scale_factor
    ACCy = ACCy_raw / scale_factor
    ACCz = ACCz_raw / scale_factor

    # Detect steps
    detect_step(ACCx, ACCy, ACCz)

    # Send step count via UDP
    message = json.dumps({"stepCount": step_count})
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
    print(f"Sent: {message}")

    # Slow down the loop to a readable pace
    time.sleep(1)  # Send data once per second
