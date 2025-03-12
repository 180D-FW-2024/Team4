import socket
import time
import threading
from telegram_bot import send_message

class Speech_Recognition_Data:
    """
    A class-based UDP receiver that listens for incoming speech recognition data
    and updates a shared state in real-time.
    """
    def __init__(self, system_manager, udp_ip="0.0.0.0", udp_port=5200):
        """
        Initialize the UDP receiver.
        :param udp_ip: IP address to bind to.
        :param udp_port: Port to bind to.
        """
        self.system_manager = system_manager
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))
        self.received_value = False  # Shared state for the latest received value
        self.lock = threading.Lock()  # Lock for thread safety
        
        self.last_received_time = time.time()
        self.activation_duration = 5  # Auto-deactivate after 5 seconds
        self.old_value = None

    def listen(self):
        print(f"Listening on {self.udp_ip}:{self.udp_port}")
        threading.Thread(target=self.check_timeout, daemon=True).start()
        
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                value = data.decode() == "1"
                
                with self.lock:  # ATOMIC UPDATE
                    self.last_received_time = time.time()
                    if self.old_value != value:
                        message = "NightWatcher Activated" if value else "NightWatcher Deactivated"
                        send_message(message)
                        self.system_manager.set_system_active(value)
                        self.old_value = value
                        
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error receiving data: {e}")

    def check_timeout(self):
        """Auto-deactivate ONLY if system was previously active"""
        while True:
            with self.lock:
                time_since_update = time.time() - self.last_received_time
                if time_since_update > self.activation_duration:
                    if self.old_value is True:  # Only deactivate if currently active
                        send_message("NightWatcher Auto-Deactivated (Timeout)")
                        self.system_manager.set_system_active(False)
                        self.old_value = False
            time.sleep(1)

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
