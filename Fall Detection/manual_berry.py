import datetime
import sys
import numpy as np
import IMU

# Sensitivity scale factors (based on datasheet)
ACC_SCALE = 0.061 * 0.00981  # mg/LSB to m/s²
GYRO_SCALE = 8.75 * 0.0000174533  # mdps/LSB to rad/s
MAG_SCALE = 0.08 * 0.1  # mGauss/LSB to μT

IMU.detectIMU()  
if IMU.BerryIMUversion == 99:
    print("No BerryIMU found... exiting")
    sys.exit()
IMU.initIMU()

print("Listening for fall events...")

while True:
    # Read sensor values
    ACCx = IMU.readACCx() * ACC_SCALE
    ACCy = IMU.readACCy() * ACC_SCALE
    ACCz = IMU.readACCz() * ACC_SCALE
    GYRx = IMU.readGYRx() * GYRO_SCALE
    GYRy = IMU.readGYRy() * GYRO_SCALE
    GYRz = IMU.readGYRz() * GYRO_SCALE
    MAGx = IMU.readMAGx() * MAG_SCALE
    MAGy = IMU.readMAGy() * MAG_SCALE
    MAGz = IMU.readMAGz() * MAG_SCALE

    # Check fall conditions
    if (
        ACCx < -20.0 or
        ACCy > 10.0 or
        ACCz > 15.0 or
        GYRx < -2.0 or
        GYRy < -3.0 or
        GYRz > 1.0
    ):
        print("Fall detected!")
        break
