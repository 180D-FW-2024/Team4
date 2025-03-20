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
    # Intializing UDP Componetns and video streaming
    RECEIVER_IP = "100.75.217.43"
    UDP_PORT = 5055
    JPEG_QUALITY = 70
    MAX_DGRAM = 65507  # Max UDP size

    # Creating UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Frame sharing between seperate threads
    latest_frame = None
    frame_lock = threading.Lock()

    send_frame_counter = 0

    # Initializing State receiver
    receiver_ip = "0.0.0.0"
    receiver_port = 8891
    rover_receiver = BooleanToggleReceiver(receiver_ip, receiver_port)
    
    receiver_thread = threading.Thread(target=rover_receiver.listen_for_state, daemon=True)
    receiver_thread.start()

    # Initializing the Motor and Camera modules
    motor = Motor()
    
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # width
    cap.set(4, 480)  # height

    if not cap.isOpened():
        print("Failed to open camera.")
        return

    # Streaming Thread for the UDP Connection
    def udp_sender():
        nonlocal send_frame_counter  

        while True:
            if rover_receiver.current_state:
                with frame_lock:
                    if latest_frame is not None:
                        send_frame_counter += 1
                        if send_frame_counter % 10 == 0:
                            # encoding the JPEG
                            _, buffer = cv2.imencode('.jpg', latest_frame, 
                                                     [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                            datagram = buffer.tobytes()
                            size = len(datagram)
                            
                            try:
                                # Sending header
                                udp_socket.sendto(struct.pack("!I", size), (RECEIVER_IP, UDP_PORT))

                                # Send packets at a time 
                                for i in range(0, size, MAX_DGRAM):
                                    chunk = datagram[i:i+MAX_DGRAM]
                                    udp_socket.sendto(chunk, (RECEIVER_IP, UDP_PORT))
                            except Exception as e:
                                print(f"UDP Send Error: {str(e)}")

            time.sleep(0.01)

    send_thread = threading.Thread(target=udp_sender, daemon=True)
    send_thread.start()

    # Main processing Loop
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

            # Updating the shared frame to main server
            with frame_lock:
                latest_frame = result

            # Logic for person detection
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

                # Motor controls
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
