import socket
import time

class BooleanToggleReceiver:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        # The current state helps track whether rover should be activated or deactivated
        self.current_state = False 
        
        # Creating and binding UDP socket for message listening
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
                    
            elif message == "False":
                if self.current_state:
                    self.current_state = False
                    print("Rover Deactivated")
                 
            else:
                print(f"Ignored unknown message: {message}")

            # Short sleep to prevent instant looping
            time.sleep(0.1)

if __name__ == "__main__":
    receiver_ip = '0.0.0.0' # or '0.0.0.0' if hostname binding does not work
    receiver_port = 8891
    rover_receiver = BooleanToggleReceiver(receiver_ip, receiver_port)
    rover_receiver.listen_for_state()
