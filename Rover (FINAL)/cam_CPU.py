import cv2
import time
from collections import deque

thres = 0.5
nms = 0.2

classNames = []
classFile = "./Object_Detection_Files/coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "./Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "./Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# Buffer to store the center of the last N bounding boxes
NUM_FRAMES = 5
centers_buffer = deque(maxlen=NUM_FRAMES)

def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)
    if len(objects) == 0:
        objects = classNames

    objectInfo = []
    if len(classIds) != 0:
        detections = list(zip(classIds.flatten(), confs.flatten(), bbox))
        # Only keep specified objects
        detections = [det for det in detections if classNames[det[0] - 1] in objects]

        if len(detections) > 0:
            # Sort by confidence
            detections.sort(key=lambda x: x[1], reverse=True)
            topDetection = detections[0]
            classId, confidence, box = topDetection
            className = classNames[classId - 1]
            objectInfo.append([box, className])

            if draw:
                cv2.rectangle(img, box, (0,255,0), 2)
                cv2.putText(img, f"{className.upper()} {round(confidence*100,2)}%", 
                            (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0,255,0), 2)
    return img, objectInfo

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to capture frame")
            break

        frame_flipped = cv2.flip(frame, 0)

        # Detect only one person
        result, objectInfo = getObjects(frame_flipped, thres, nms, objects=["person"])

        # If we have a bounding box, track its center
        if objectInfo:
            box, className = objectInfo[0]
            x, y, w, h = box
            center = (x + w//2, y + h//2)
            centers_buffer.append(center)

            # Check how much the center has moved in the last NUM_FRAMES
            if len(centers_buffer) == NUM_FRAMES:
                # Compute total displacement from oldest to newest
                (old_x, old_y) = centers_buffer[0]
                (new_x, new_y) = centers_buffer[-1]
                displacement = ((new_x - old_x)**2 + (new_y - old_y)**2)**0.5

                # If displacement is very small, assume it's not a real moving person
                if displacement < 20:  # tune as needed
                    print("Likely an inanimate object (no movement).")
                else:
                    print(f"Detected moving {className} with box {box}")
            else:
                print(f"Gathering movement data... center={center}")
        else:
            # No person => clear movement data, stop
            centers_buffer.clear()
            print("No person detected.")

        cv2.imshow("CAM_CPU", result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
