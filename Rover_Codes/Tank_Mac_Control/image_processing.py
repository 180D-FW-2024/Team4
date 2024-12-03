import os
import cv2
import numpy as np
import pygame
from datetime import datetime

from phycv.vevid_superfast import VEVID_Superfast
from phycv.vevid_superfast_bgr import VEVID_Superfast_BGR
from phycv.pst import PST

# Control Variable(s):
save_picture = False
save_picture_watermark = 100

# Global Variables
vevid_superfast = VEVID_Superfast()
vevid_superfast_bgr = VEVID_Superfast_BGR()

def pst_run(image):
    S = 0.3
    W = 15
    sigma_LPF = 0.15
    thresh_min = 0.05
    thresh_max = 0.9
    morph_flag = 1
    img = PST().runArray(
        img_array=cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
        S=S,
        W=W,
        sigma_LPF=sigma_LPF,
        thresh_min=thresh_min,
        thresh_max=thresh_max,
        morph_flag=morph_flag,
    )
    gray_pst = cv2.convertScaleAbs(img, alpha=255.0)
    return cv2.cvtColor(gray_pst, cv2.COLOR_GRAY2BGR)

# Save frames into .png files
def save_frame(frame):
    # Define the output directory
    output_dir = 'output_picts'
    
    # Check if the directory exists; if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the current time
    now = datetime.now()
    # Format the time to the desired format
    file_name = f"{now.year}_{now.month:02}_{now.day:02}_{now.hour:02}{now.minute:02}{now.second:02}.png"

    # Combine the directory path and the filename
    file_path = os.path.join(output_dir, file_name)

    # Save the frame
    cv2.imwrite(file_path, frame)

# Object Detection Variables
classNames = []
classFile = "./Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "./Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "./Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


def getObjects(img, thres, nms, draw=True, objects=[]):
    # Object Detection
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    #print(classIds,bbox)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
    return img,objectInfo

# Frame processing
def image_process(frame, input_ctrl, turn_on_obj, movement, motor_speed, max_speed):
    global save_picture
    global save_picture_watermark

    retVal = cv2.flip(cv2.flip(frame, 1), 0)
    if input_ctrl == "Adaptive VEViD":
        retVal = vevid_superfast.apply_adaptive_vevid_lut(retVal)
    elif input_ctrl == "Adaptive VEViD BGR":
        retVal = vevid_superfast_bgr.apply_adaptive_vevid_lut(retVal)
    elif input_ctrl == "PST":
        retVal = pst_run(retVal)
    if turn_on_obj:
        retVal, _ = getObjects(retVal, 0.5, 0.2)

    # Choose text color based on algorithm running
    text_color = (0, 255, 0)  # Default Green color
    if input_ctrl == "PST":
        text_color = (255, 255, 255)  # White color

    # Choose smaller font size and thickness for lower resolution
    font_scale = 0.5  # Adjusted from 1 to 0.5
    thickness = 1  # Adjusted from 2 to 1

    # Adjust text position and size for 360p resolution
    base_line_height = 20  # Base line height for the first line of text
    line_gap = 15  # Gap between lines of text

    # Draw the current mode and object detection status on the frame
    obj_status = "Object Detection: ON" if turn_on_obj else "Object Detection: OFF"
    cv2.putText(retVal, f"Mode: {input_ctrl}", (10, base_line_height), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)
    cv2.putText(retVal, obj_status, (10, base_line_height + line_gap), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)
    cv2.putText(retVal, f"Movement: {movement}", (260, base_line_height), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)
    cv2.putText(retVal, f"Speed: [{motor_speed[0]}%, {motor_speed[1]}%]", (260, base_line_height + line_gap), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)
    cv2.putText(retVal, f"Max Speed: {max_speed}%", (260, base_line_height + (2 * line_gap)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)
    
    if save_picture:
        save_picture = False
        save_frame(retVal)
    if save_picture_watermark < 15:
        cv2.putText(retVal, f"Frame Saved", (500, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
        save_picture_watermark += 1
    else:
        save_picture_watermark = 100

    return retVal


# Display image with cv2
def display_image(image_path):
    # Read the image
    img = cv2.imread(image_path)

    # Check if the image was loaded successfully
    if img is None:
        print("Error: Couldn't load the image.")
        return

    # Name the window
    window_name = "MonkiCorp"

    # Display the image in the window for 3 seconds
    cv2.imshow(window_name, img)
    cv2.waitKey(3000)

    # Destroy the window after the key press
    cv2.destroyAllWindows()

# Control the input
def input_control(keys, visual_ctrl, turn_on_obj):
    global save_picture
    global save_picture_watermark

    # Input Control for image processing
    if keys[pygame.K_0]:
        return "NORMAL", turn_on_obj
    if keys[pygame.K_1]:
        return "Adaptive VEViD", turn_on_obj
    if keys[pygame.K_2]:
        return "Adaptive VEViD BGR", turn_on_obj
    if keys[pygame.K_3]:
        if turn_on_obj is True:
            return "PST", False
        return "PST", turn_on_obj
    if keys[pygame.K_o]:
        if visual_ctrl == "PAGE" or visual_ctrl == "PST":
            return visual_ctrl, False
        turn_on_obj = not turn_on_obj
        return visual_ctrl, turn_on_obj
    if keys[pygame.K_p]:
        save_picture = True
        save_picture_watermark = 0

    return visual_ctrl, turn_on_obj
