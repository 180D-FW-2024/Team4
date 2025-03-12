# video_rover_receiver.py
import socket
import struct
import cv2
import numpy as np
import threading

class VideoRoverReceiver:
    def __init__(self, udp_ip="0.0.0.0", udp_port=5055):
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))
        
    def run(self):
        """Main reception loop"""
        self.running = True
        while self.running:
            try:
                # Receive header first (4 bytes for frame size)
                header_data, _ = self.sock.recvfrom(4)
                frame_size = struct.unpack("!I", header_data)[0]
                
                # Accumulate frame data
                datagram = b''
                while len(datagram) < frame_size:
                    chunk, _ = self.sock.recvfrom(65535)
                    datagram += chunk

                # Decode and store frame
                frame = cv2.imdecode(np.frombuffer(datagram, np.uint8), cv2.IMREAD_COLOR)
                print("Rover camera received")
                with self.frame_lock:
                    self.latest_frame = frame.copy()  # Store a copy to prevent mutation

            except Exception as e:
                if self.running:
                    print(f"Video reception error: {str(e)}")

    def get_latest_frame(self):
        """Thread-safe access to latest frame"""
        with self.frame_lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def stop(self):
        """Cleanup resources"""
        self.running = False
        self.sock.close()
