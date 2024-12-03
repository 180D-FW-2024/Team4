import socket

# Define the UDP IP and port
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 5200

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Waiting for data...")

try:
    while True:
        # Receive the data
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        
        # Decode the message and interpret as a boolean
        boolean_value = True if data.decode() == "1" else False
        print(f"Received: {boolean_value} from {addr}")

except KeyboardInterrupt:
    print("Receiver stopped.")

finally:
    sock.close()
