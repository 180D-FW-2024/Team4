import datetime
import sys
import numpy as np
import IMU
import time
import math
import json
import socket
import os
 
###### PORT AND IP ###################################
UDP_IP = "100.75.217.43"  # Receiver's IP (main Raspberry Pi)
UDP_PORT_FALL = 5001      
UDP_PORT_STEP = 5005    
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

############ VARIABLES ####################################

# Sensitivity scale factors (based on datasheet)
ACC_SCALE = 0.061 * 0.00981  # mg/LSB to m/s²
GYRO_SCALE = 8.75 * 0.0000174533  # mdps/LSB to rad/s
MAG_SCALE = 0.08 * 0.1  # mGauss/LSB to μT

#STEP COUNTER
previous_magnitude = 0
step_count = 0
threshold = 0.3  # Adjust this based on testing
last_step_count = 0
last_step_time = 0  # Tracks the time of the last detected step
debounce_interval = 0.3  # Minimum time between steps in seconds
noise_threshold = 1.5 
alpha = 0.01
RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40      # Complementary filter constant
min_step_interval = 0.2
filtered_ACCx = 0
filtered_ACCy = 0
filtered_ACCz = 0
################ FALL DETECTION #########################

IMU.detectIMU()  
if IMU.BerryIMUversion == 99:
    print("No FALL BerryIMU found... exiting")
    sys.exit()
IMU.initIMU()

print("Listening for fall events...")


################# STEP COUNTER ####################
################# Compass Calibration values ############
# Use calibrateBerryIMU.py to get calibration values
# Calibrating the compass isnt mandatory, however a calibrated
# compass will result in a more accurate heading value.

magXmin =  0
magYmin =  0
magZmin =  0
magXmax =  0
magYmax =  0
magZmax =  0


'''
Here is an example:
magXmin =  -1748
magYmin =  -1025
magZmin =  -1876
magXmax =  959
magYmax =  1651
magZmax =  708
Dont use the above values, these are just an example.
'''
############### END Calibration offsets #################


#Kalman filter variables
Q_angle = 0.02
Q_gyro = 0.0015
R_angle = 0.005
y_bias = 0.0
x_bias = 0.0
XP_00 = 0.0
XP_01 = 0.0
XP_10 = 0.0
XP_11 = 0.0
YP_00 = 0.0
YP_01 = 0.0
YP_10 = 0.0
YP_11 = 0.0
KFangleX = 0.0
KFangleY = 0.0

def check_walking():
    """
    Checks if the step count is greater than 1 and returns 'walking' if true.
    """
    if step_count > 1:
        return "started walking"
    else:
        return "not walking"


def detect_step(ACCx, ACCy, ACCz):
    global previous_magnitude, step_count, last_step_time, threshold

    # Calculate the magnitude of acceleration
    magnitude = math.sqrt(ACCx**2 + ACCy**2 + ACCz**2)

    # Debugging: Print magnitude values
   # print(f"Raw Magnitude: {magnitude}, Threshold: {threshold}")

    # Ignore small values below threshold
    if magnitude < threshold:
        return

    # Apply exponential moving average for smoothing
    smoothed_magnitude = 0.8 * previous_magnitude + 0.2 * magnitude
    previous_magnitude = smoothed_magnitude

    # Debugging: Print smoothed magnitude
    #print(f"Smoothed Magnitude: {smoothed_magnitude}")

    # Update dynamic threshold
    threshold = (1 - alpha) * threshold + alpha * magnitude

    # Time filter: Avoid duplicate step counts
    current_time = time.time()
    if smoothed_magnitude > threshold and (current_time - last_step_time > min_step_interval):
        step_count += 1
        last_step_time = current_time
        print(f"Step detected! Total steps: {step_count}")

    previous_magnitude = smoothed_magnitude


def kalmanFilterY ( accAngle, gyroRate, DT):
    y=0.0
    S=0.0

    global KFangleY
    global Q_angle
    global Q_gyro
    global y_bias
    global YP_00
    global YP_01
    global YP_10
    global YP_11

    KFangleY = KFangleY + DT * (gyroRate - y_bias)

    YP_00 = YP_00 + ( - DT * (YP_10 + YP_01) + Q_angle * DT )
    YP_01 = YP_01 + ( - DT * YP_11 )
    YP_10 = YP_10 + ( - DT * YP_11 )
    YP_11 = YP_11 + ( + Q_gyro * DT )

    y = accAngle - KFangleY
    S = YP_00 + R_angle
    K_0 = YP_00 / S
    K_1 = YP_10 / S

    KFangleY = KFangleY + ( K_0 * y )
    y_bias = y_bias + ( K_1 * y )

    YP_00 = YP_00 - ( K_0 * YP_00 )
    YP_01 = YP_01 - ( K_0 * YP_01 )
    YP_10 = YP_10 - ( K_1 * YP_00 )
    YP_11 = YP_11 - ( K_1 * YP_01 )

    return KFangleY

def kalmanFilterX ( accAngle, gyroRate, DT):
    x=0.0
    S=0.0

    global KFangleX
    global Q_angle
    global Q_gyro
    global x_bias
    global XP_00
    global XP_01
    global XP_10
    global XP_11


    KFangleX = KFangleX + DT * (gyroRate - x_bias)

    XP_00 = XP_00 + ( - DT * (XP_10 + XP_01) + Q_angle * DT )
    XP_01 = XP_01 + ( - DT * XP_11 )
    XP_10 = XP_10 + ( - DT * XP_11 )
    XP_11 = XP_11 + ( + Q_gyro * DT )

    x = accAngle - KFangleX
    S = XP_00 + R_angle
    K_0 = XP_00 / S
    K_1 = XP_10 / S

    KFangleX = KFangleX + ( K_0 * x )
    x_bias = x_bias + ( K_1 * x )

    XP_00 = XP_00 - ( K_0 * XP_00 )
    XP_01 = XP_01 - ( K_0 * XP_01 )
    XP_10 = XP_10 - ( K_1 * XP_00 )
    XP_11 = XP_11 - ( K_1 * XP_01 )

    return KFangleX


IMU.detectIMU()     #Detect if BerryIMU is connected.
if(IMU.BerryIMUversion == 99):
    print(" No STEP BerryIMU found... exiting ")
    sys.exit()
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0
kalmanX = 0.0
kalmanY = 0.0

a = datetime.datetime.now()

walking_started = False
previous_step_count = -1

while True:
    # Example: Set the scale factor based on a ±2g configuration
    scale_factor = 16384  # For ±2g range

# Read raw accelerometer data from the IMU
    ACCx_raw = IMU.readACCx()  # Replace with your actual IMU reading function
    ACCy_raw = IMU.readACCy()
    ACCz_raw = IMU.readACCz()

# Normalize the raw data to real-world units (g)
    ACCx = ACCx_raw / scale_factor
    ACCy = ACCy_raw / scale_factor
    ACCz = ACCz_raw / scale_factor


    #Read the accelerometer,gyroscope and magnetometer values
    GYRx = IMU.readGYRx()
    GYRy = IMU.readGYRy()
    GYRz = IMU.readGYRz()
    MAGx = IMU.readMAGx()
    MAGy = IMU.readMAGy()
    MAGz = IMU.readMAGz()


    #Apply compass calibration
    MAGx -= (magXmin + magXmax) /2
    MAGy -= (magYmin + magYmax) /2
    MAGz -= (magZmin + magZmax) /2


    ##Calculate loop Period(LP). How long between Gyro Reads
    b = datetime.datetime.now() - a
    a = datetime.datetime.now()
    LP = b.microseconds/(1000000*1.0)
    outputString = "Loop Time %5.2f " % ( LP )



    #Convert Gyro raw to degrees per second
    rate_gyr_x =  GYRx * G_GAIN
    rate_gyr_y =  GYRy * G_GAIN
    rate_gyr_z =  GYRz * G_GAIN


    #Calculate the angles from the gyro.
    gyroXangle+=rate_gyr_x*LP
    gyroYangle+=rate_gyr_y*LP
    gyroZangle+=rate_gyr_z*LP



   #Convert Accelerometer values to degrees
    AccXangle =  (math.atan2(ACCy,ACCz)*RAD_TO_DEG)
    AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG

    #convert the values to -180 and +180
    if AccYangle > 90:
        AccYangle -= 270.0
    else:
        AccYangle += 90.0


    #Complementary filter used to combine the accelerometer and gyro values.
    CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
    CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle

    #Kalman filter used to combine the accelerometer and gyro values.
    kalmanY = kalmanFilterY(AccYangle, rate_gyr_y,LP)
    kalmanX = kalmanFilterX(AccXangle, rate_gyr_x,LP)


    #Calculate heading
    heading = 180 * math.atan2(MAGy,MAGx)/M_PI

    #Only have our heading between 0 and 360
    if heading < 0:
        heading += 360





    ####################################################################
    ###################Tilt compensated heading#########################
    ####################################################################
    #Normalize accelerometer raw values.
    accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
    accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)


    #Calculate pitch and roll
    pitch = math.asin(accXnorm)
    roll = -math.asin(accYnorm/math.cos(pitch))


    #Calculate the new tilt compensated values
    #The compass and accelerometer are orientated differently on the the BerryIMUv1, v2 and v3.
    #This needs to be taken into consideration when performing the calculations

    #X compensation
    if(IMU.BerryIMUversion == 1 or IMU.BerryIMUversion == 3):            #LSM9DS0 and (LSM6DSL & LIS2MDL)
        magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
    else:                                                                #LSM9DS1
        magXcomp = MAGx*math.cos(pitch)-MAGz*math.sin(pitch)

    #Y compensation
    if(IMU.BerryIMUversion == 1 or IMU.BerryIMUversion == 3):            #LSM9DS0 and (LSM6DSL & LIS2MDL)
        magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)
    else:                                                                #LSM9DS1
        magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)+MAGz*math.sin(roll)*math.cos(pitch)




    #Calculate tilt compensated heading
    tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI

    if tiltCompensatedHeading < 0:
        tiltCompensatedHeading += 360


    ##################### END Tilt Compensation ########################

    # Detect steps
    detect_step(ACCx, ACCy, ACCz)  # Call the step detection function


    status = check_walking()

    if status == "started walking" and not walking_started:
        print(f"Status: {status}")
        walking_started = True
    elif status != "started walking":
        walking_started = False

    if step_count > previous_step_count:
        outputString += f"\t# Steps: {step_count} #"
        message = json.dumps({"stepCount": step_count})
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT_STEP))
        print(f"Sent: {message}")

        previous_step_count = step_count

    #slow program down a bit, makes the output more readable
    time.sleep(0.03)

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
        ACCx < -18.0 or #-20, -17
        ACCy > 9.0 or #10, 8
        ACCz > 14.5 or #15, 14
        GYRx < -1.8 or #-2, -1.7
        GYRy < -2.9 or #-3, -2.8
        GYRz > 0.9 #1, 0.8
    ):
        fall_detect = 1
        print("Fall detected!")
        message = json.dumps({"fallDetected": fall_detect})
        sock.sendto(message.encode('utf-8'), (UDP_IP, UDP_PORT_FALL))
        #break
