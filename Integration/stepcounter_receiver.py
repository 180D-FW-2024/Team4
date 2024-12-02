import socket
import json

# Define the UDP IP and port
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 5005     # Ensure this matches the sender's port

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Waiting for step count data...")

try:
    while True:
        # Receive the data
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        
        try:
            # Decode the message and interpret as JSON
            json_data = json.loads(data.decode('utf-8'))
            
            # Extract the step count
            step_count = json_data.get("stepCount", 0)
            print(f"Received step count: {step_count} from {addr}")
        
        except json.JSONDecodeError:
            print(f"Invalid data received from {addr}: {data.decode('utf-8')}")

except KeyboardInterrupt:
    print("Receiver stopped.")

finally:
    sock.close()
