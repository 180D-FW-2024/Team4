import cv2
from ultralytics import YOLO
from rover_activation import rover_toggle
from phycv.vlight import VLight

class Camera:
    """
    Encapsulates the camera system for YOLO-based object detection.
    """
    def __init__(self, model_path='yolov8n.pt', camera_index=0):
        self.model = YOLO(model_path)  # Load YOLO model
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)
        self.object_detected = False
        self.object_coordinates = []  # Stores the coordinates of detected objects
        self.vlight = VLight()
        self.annotated_frame = None

    def get_annotated_frame(self):
        return self.annotated_frame
       
    def run(self):
        """
        Start the camera loop and perform detection.
        """
        if not self.cap.isOpened():
            print("Error: Could not open video stream.")
            return

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to capture image.")
                break

            # VLight PhyCV Low-Light Enhancement
            frame = self.vlight.run_img_array(frame, v=0.5, color=False, lut=True)

            # Perform inference with class filtering for 'person' class (class 0)
            results = self.model.predict(source=frame, classes=[0])
            detections = results[0].boxes  # Get detected boxes

            # Check if any objects are detected
            self.object_detected = len(detections) > 0
            self.object_coordinates = []

            # Extract coordinates if detections exist
            if self.object_detected:
                for box in detections:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()  # Get bounding box coordinates
                    self.object_coordinates.append((x1, y1, x2, y2))  # Append to the list

                if rover_toggle.getcurrentState() is True:
                    rover_toggle.toggle_and_send()
            else:
                if rover_toggle.getcurrentState() is False:
                    rover_toggle.toggle_and_send()

            # Visualize the results on the frame
            self.annotated_frame = results[0].plot()

            # Display the frame
            # cv2.imshow('Person Detection', annotated_frame)

            # Print detection information (optional for debugging)
            print(f"Detected: {self.object_detected}, Coordinates: {self.object_coordinates}")

            # Exit loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
