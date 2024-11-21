import cv2
import socket
import numpy as np
import threading

def send_frames_to_udp(server_address, terminate, width=640, height=480, quality=50):
    camera = cv2.VideoCapture(0)
    camera.set(3, width)
    camera.set(4, height)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        while not terminate.is_set():
            ret, frame = camera.read()
            if not ret:
                print("Failed to grab frame")
                break
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            sock.sendto(buffer.tobytes(), server_address)
    finally:
        camera.release()
        sock.close()
