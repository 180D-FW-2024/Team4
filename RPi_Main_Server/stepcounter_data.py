import socket
import json
import threading
import time
from telegram_bot import send_message

class StepCounterReceiver:
    """
    A class-based UDP receiver that listens for incoming step count data
    and updates a shared state in real-time.
    """
    def __init__(self, system_manager, udp_ip="0.0.0.0", udp_port=5005):
        """
        Initialize the UDP receiver for step count data.
        :param udp_ip: IP address to bind to.
        :param udp_port: Port to bind to.
        """
        self.system_manager = system_manager
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))
        self.step_count = 0  # Shared state for the latest step count
        self.lock = threading.Lock()  # Lock for thread safety

    def listen(self):
        """
        Continuously listens for incoming UDP messages.
        Updates the shared step count in real-time.
        """
        print(f"Listening for step count data on {self.udp_ip}:{self.udp_port}")
        while True:
            # Receive the data
            data, addr = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes

            while not self.system_manager.get_system_active():
                time.sleep(0.1)
                print("Step Counter Paused")

            # Decode the message and interpret as JSON
            json_data = json.loads(data.decode('utf-8'))
            
            # Extract the step count
            step_count = json_data.get("stepCount", 0)

            # Update the shared step count
            with self.lock:
                if self.step_count != step_count:
                    send_message(f"StepCount={step_count}")
                self.step_count = step_count

            # Debug output
            print(f"Received step count: {step_count} from {addr}")

    def get_step_count(self):
        """
        Get the latest step count in a thread-safe way.
        :return: The latest step count.
        """
        with self.lock:
            return self.step_count

    def run(self):
        """
        Start the UDP receiver in a separate thread.
        """
        listen_thread = threading.Thread(target=self.listen, name="UDPListenThread", daemon=True)
        listen_thread.start()
