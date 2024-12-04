import socket
import time
from telegram_bot import send_message
from alarm import ring_alarm

class BooleanToggleSender:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.current_state = False  # Start with False

    def toggle_and_send(self):
        # Toggle the state
        self.current_state = not self.current_state
        message = "True" if self.current_state else "False"
        if self.current_state is True:
            send_message(message="Rover Activated")
            ring_alarm()
        elif self.current_state is False:
            send_message(message="Rover Deactivated")
            
        # Send the message
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(message.encode('utf-8'), (self.ip_address, self.port))
            print(f"Sent: {message} to {self.ip_address}:{self.port}")
        finally:
            sock.close()
        
    def getcurrentState(self):
        return self.current_state

# Replace '192.168.1.50' with the IP address of the device running the listener
receiver_ip = "192.168.245.59"
receiver_port = 8891
rover_toggle = BooleanToggleSender(receiver_ip, receiver_port)
