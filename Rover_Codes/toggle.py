import socket
import time

class BooleanToggleSender:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.current_state = False  # Start with False

    def toggle_and_send(self):
        # Toggle the state
        self.current_state = not self.current_state
        message = "True" if self.current_state else "False"

        # Send the message
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(message.encode('utf-8'), (self.ip_address, self.port))
            print(f"Sent: {message} to {self.ip_address}:{self.port}")
        finally:
            sock.close()

# Replace '192.168.1.50' with the IP address of the device running the listener
receiver_ip = "192.168.1.96"
receiver_port = 8891  # Port on which the listener is running

if __name__ == "__main__":
    sender = BooleanToggleSender(receiver_ip, receiver_port)
    a = None
    while (a != "q"):
        a = input("Input here: ")
        if (a == "a"):
            sender.toggle_and_send()

