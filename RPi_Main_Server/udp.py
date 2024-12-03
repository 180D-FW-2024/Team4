import socket
import json
import threading
import time
from telegram_bot import *
#from udp_eduardo import UDPSpeechHandler  # Import the speech handler

class UDPHandler:
    """
    Handles UDP communication for receiving and sending JSON data.
    """
    def __init__(self, receive_host='0.0.0.0', receive_port=5005, default_send_host='127.0.0.1', default_send_port=6006):
        """
        Initialize the UDP handler.
        :param receive_host: Host address to bind for receiving.
        :param receive_port: Port to bind for receiving.
        :param default_send_host: Default host address for sending.
        :param default_send_port: Default port for sending.
        """
        self.receive_host = receive_host
        self.receive_port = receive_port
        self.default_send_host = default_send_host
        self.default_send_port = default_send_port

        # Create UDP sockets
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket.bind((self.receive_host, self.receive_port))

        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Shared state variables
        self.system_on = False
        self.fall_detected = False
        self.num_steps = 0
        self.rover_on = False

        # Lock for thread safety
        self.lock = threading.Lock()

    def receive_data(self):
        """
        Receive JSON data over UDP and update state variables.
        """
        while True:
            try:
                data, addr = self.recv_socket.recvfrom(1024)  # Receive 1024 bytes
                json_data = json.loads(data.decode('utf-8'))
                print(f"Received data: {json_data} from {addr}")

                # Update state variables only if they are present
                with self.lock:
                    if "systemOn" in json_data:
                        self.system_on = json_data["systemOn"]
                        if self.systemOn is True:
                            print("System is On")
                    if "fallDetection" in json_data:
                        self.fall_detected = json_data["fallDetected"]
                        if self.fall_detected:
                            print("Fall Detected")
                    if "numSteps" in json_data:
                        self.num_steps = json_data["numSteps"]
                        if self.num_steps > 0:
                            print(num_steps)

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Error parsing JSON: {e}")

    def send_data(self, json_data, ip_address, port):
        """
        Send JSON data over UDP to a specific IP address and port.
        :param json_data: The JSON data to send as a dictionary.
        :param ip_address: The target IP address.
        :param port: The target port.
        """
        try:
            self.send_socket.sendto(json.dumps(json_data).encode('utf-8'), (ip_address, port))
            print(f"Sent data to {ip_address}:{port} -> {json_data}")
        except Exception as e:
            print(f"Error sending data: {e}")

    def send_periodic_data(self):
        """
        Periodically send default JSON data over UDP.
        """
        while True:
            try:
                with self.lock:
                    send_json = {
                        "roverOn": self.rover_on
                    }
                self.send_data(send_json, self.default_send_host, self.default_send_port)
                time.sleep(1)  # Adjust interval as needed
            except Exception as e:
                print(f"Error in periodic sending: {e}")

    def run(self):
        """
        Start UDP communication for receiving and sending in separate threads.
        """
        receive_thread = threading.Thread(target=self.receive_data, name="UDPReceiveThread", daemon=True)
        periodic_send_thread = threading.Thread(target=self.send_periodic_data, name="UDPSendThread", daemon=True)

        receive_thread.start()
        periodic_send_thread.start()

        receive_thread.join()
        periodic_send_thread.join()
