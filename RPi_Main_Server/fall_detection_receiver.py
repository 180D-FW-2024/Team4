# fall_detection_receiver.py
import socket
import json
import threading
import time
from telegram_bot import send_message

class FallDetectionReceiver:
    """
    Fixed UDP receiver with proper threading implementation
    """
    def __init__(self, system_manager, udp_ip="0.0.0.0", udp_port=5001):
        self.system_manager = system_manager
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.udp_ip, self.udp_port))
        self.running = True
        self.thread = None

    def run(self):
        """Main entry point to start the receiver"""
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def _listen_loop(self):
        """Internal listening loop"""
        print(f"Fall detection initialized on {self.udp_ip}:{self.udp_port}")
        while self.running:
            while not self.system_manager.get_system_active():
                time.sleep(0.1)
                print("Fall Detection Paused")
                
            data, addr = self.sock.recvfrom(1024)
            json_data = json.loads(data.decode('utf-8'))
            
            if json_data.get("fallDetected", False):
                print("Fall detected! Sending Telegram alert.")
                send_message("🚨 EMERGENCY: Fall detected!")

    def stop(self):
        """Clean shutdown"""
        self.running = False
        self.sock.close()
        if self.thread:
            self.thread.join()
