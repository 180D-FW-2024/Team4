import cv2
import time
import threading
import socket
import struct
import numpy as np

from receiver import BooleanToggleReceiver
from cam_CPU import getObjects, thres, nms, classNames
from motor import Motor

def main():
    # ----------------------------------------------------
    # 1) Initialize UDP Components
    # ----------------------------------------------------
    # Video streaming configuration
    RECEIVER_IP = "100.75.217.43"
    UDP_PORT = 5055
    JPEG_QUALITY = 70
    MAX_DGRAM = 65507  # Max UDP payload size

    # Create UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Frame sharing between threads
    latest_frame = None
    frame_lock = threading.Lock()

    # ----------------------------------------------------
    # 2) Initialize State Receiver
    # ----------------------------------------------------
    receiver_ip = "0.0.0.0"
    receiver_port = 8891
    rover_receiver = BooleanToggleReceiver(receiver_ip, receiver_port)
    
    receiver_thread = threading.Thread(target=rover_receiver.listen_for_state, daemon=True)
    receiver_thread.start()

    # ----------------------------------------------------
    # 3) Initialize Motor and Camera
    # ----------------------------------------------------
    motor = Motor()
    
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # width
    cap.set(4, 480)  # height

    if not cap.isOpened():
        print("Failed to open camera.")
        return

    # ----------------------------------------------------
    # 4) UDP Streaming Thread
    # ----------------------------------------------------
    def udp_sender():
        while True:
            if rover_receiver.current_state:
                with frame_lock:
                    if latest_frame is not None:
                        # JPEG encode
                        _, buffer = cv2.imencode('.jpg', latest_frame, 
                                            [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                        datagram = buffer.tobytes()
                        size = len(datagram)
                        
                        try:
                            # Send header
                            udp_socket.sendto(struct.pack("!I", size), (RECEIVER_IP, UDP_PORT))
                            # Send chunks
                            for i in range(0, size, MAX_DGRAM):
                                chunk = datagram[i:i+MAX_DGRAM]
                                udp_socket.sendto(chunk, (RECEIVER_IP, UDP_PORT))
                        except Exception as e:
                            print(f"UDP Send Error: {str(e)}")
            time.sleep(0.01)

    send_thread = threading.Thread(target=udp_sender, daemon=True)
    send_thread.start()

    # ----------------------------------------------------
    # 5) Main Processing Loop
    # ----------------------------------------------------
    print("[INFO] Starting main loop. Rover will wait for activation signal...")

    try:
        while True:
            if not rover_receiver.current_state:
                motor.stop()
                print("[INFO] Rover is Deactivated. Waiting for 'True' toggle...")
                time.sleep(0.1)
                continue

            success, frame = cap.read()
            if not success:
                print("Failed to capture frame.")
                break

            frame_flipped = cv2.flip(frame, 0)
            result, objectInfo = getObjects(frame_flipped, thres, nms, objects=["person"])

            # Update shared frame
            with frame_lock:
                latest_frame = result

            # Person detection logic
            if objectInfo:
                box, className = objectInfo[0]
                x, y, w, h = box
                area = w * h
                center_x = x + w // 2
                frame_center_x = frame_flipped.shape[1] // 2
                offset_x = center_x - frame_center_x
                half_width = frame_flipped.shape[1] / 2.0
                offset_norm = offset_x / half_width
                turn_val = offset_norm * 0.6

                # Motor control
                forward_val = 0.4 if area > 50000 else -0.4
                left_motor = max(min(forward_val - turn_val, 0.5), -0.5)
                right_motor = max(min(forward_val + turn_val, 0.5), -0.5)
                
                motor.drive_ugv02_motor(left_motor, right_motor)
                print(f"Tracking: Area={area}, L={left_motor:.2f}, R={right_motor:.2f}")
            else:
                motor.stop()
                print("No person detected")

            cv2.imshow("Person Follow", result)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        motor.stop()
        udp_socket.close()
        print("[INFO] Cleanup complete")

if __name__ == "__main__":
    main()
