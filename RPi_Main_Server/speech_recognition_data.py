import socket
import threading
from telegram_bot import send_message

class Speech_Recognition_Data:
    """
    A class-based UDP receiver that listens for incoming speech recognition data
    and updates a shared state in real-time.
    """
    def __init__(self, udp_ip="0.0.0.0", udp_port=5200):
        """
        Initialize the UDP receiver.
        :param udp_ip: IP address to bind to.
        :param udp_port: Port to bind to.
        """
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))
        self.received_value = False  # Shared state for the latest received value
        self.lock = threading.Lock()  # Lock for thread safety

    def listen(self):
        """
        Continuously listens for incoming UDP messages.
        Updates the shared state in real-time.
        """
        print(f"Listening on {self.udp_ip}:{self.udp_port}")
        oldValue = None
        while True:
            try:
                # Receive data
                data, addr = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
                
                # Decode the message and interpret as a boolean
                value = True if data.decode() == "1" else False
                message = "NightWatcher Activated" if value else "NightWatcher Deactivated"

                if oldValue is None:
                    send_message(message=message)
                    oldValue = value
                else:
                    if (oldValue != value):
                        send_message(message=message)
                        oldValue = value
                        
                # Update the shared state
                with self.lock:
                    self.received_value = value
                
                
            except Exception as e:
                print(f"Error receiving data: {e}")

    def get_value(self):
        """
        Get the latest received value in a thread-safe way.
        :return: The latest received value (True/False).
        """
        with self.lock:
            return self.received_value

    def run(self):
        """
        Start the UDP receiver in a separate thread.
        """
        listen_thread = threading.Thread(target=self.listen, name="UDPListenThread", daemon=True)
        listen_thread.start()
