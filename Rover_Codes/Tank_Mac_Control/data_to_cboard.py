import json
import socket

# Function to send integers
def send_integer_to_rpi(sock, value, address):
    sock.sendto(str(value).encode('utf-8'), address)

def send_motor_speed(server_address, motor_speed):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Serialize the list to JSON format
    motor_speed_json = json.dumps(motor_speed)

    # Send data
    sock.sendto(motor_speed_json.encode('utf-8'), server_address)

    # Close the socket
    sock.close()
