import socket
import time

class BooleanToggleReceiver:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.current_state = False  # Tracks whether the rover should be active or not
        
        # Create and bind a UDP socket to listen for messages
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # If .local resolution is supported, binding directly by hostname may work:
        # Alternatively, you can bind to '0.0.0.0' to listen on all interfaces:
        self.sock.bind((self.ip_address, self.port))
        
        print(f"Listening on {self.ip_address}:{self.port} for toggle messages...")

    def listen_for_state(self):
        """
        Continuously listen for incoming 'True' or 'False' messages.
        If the state changes, activate/deactivate the rover.
        """
        while True:
            data, addr = self.sock.recvfrom(1024)  # Buffer size of 1024 bytes
            message = data.decode('utf-8').strip()
            print(f"Received: {message} from {addr}")

            if message == "True":
                if not self.current_state:
                    self.current_state = True
                    print("Rover Activated")
                    # Insert logic to start/enable the rover here
                    # e.g., motor.start() or similar
            elif message == "False":
                if self.current_state:
                    self.current_state = False
                    print("Rover Deactivated")
                    # Insert logic to stop/disable the rover here
                    # e.g., motor.stop() or similar
            else:
                print(f"Ignored unknown message: {message}")

            # Short sleep to prevent tight looping
            time.sleep(0.1)

if __name__ == "__main__":
    receiver_ip = '0.0.0.0' # or '0.0.0.0' if hostname binding does not work
    receiver_port = 8891
    rover_receiver = BooleanToggleReceiver(receiver_ip, receiver_port)
    rover_receiver.listen_for_state()
