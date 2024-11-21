import socket
import json
import threading
import serial
import json

# Initialize the serial connection
try:
    ser = serial.Serial('/dev/serial0', baudrate=1000000, timeout=1)
except serial.SerialException as e:
    print("Error opening the serial port: {}".format(e))
    exit()

def receive_integer(port, timeout=0.1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    sock.settimeout(timeout)

    try:
        data, _ = sock.recvfrom(1024)
        return int(data.decode('utf-8'))
    except socket.timeout:
        return None
    finally:
        sock.close()


def send_command_to_ugv02(left_power, right_power):
    # Normalize and scale the power values from -1.0...+1.0 to -255...+255 range
    left_power_scaled = int(left_power * 255)
    right_power_scaled = int(right_power * 255)
    
    # Clamp the values to ensure they're within the -255 to +255 bounds after scaling
    left_power_scaled = max(min(left_power_scaled, 255), -255)
    right_power_scaled = max(min(right_power_scaled, 255), -255)

    # Create the command JSON object
    command = {
        "T": 1,  # Movement control command type
        "L": left_power_scaled,
        "R": right_power_scaled
    }

    # Send the command JSON over UART as a string followed by a newline
    command_json = json.dumps(command) + '\n'
    try:
        ser.write(command_json.encode('utf-8'))
    except Exception as e:
        print(f"Error sending command to UGV02: {e}")



def receive_motor_speed(port, terminate):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    sock.settimeout(0.1)  # add timeout for consistency
    
    prev_speed = [0.0, 0.0]
    try:
        while not terminate.is_set():  # using is_set() method to check the flag
            try:
                data, _ = sock.recvfrom(1024)
                motor_speed = json.loads(data.decode('utf-8'))
                prev_speed = motor_speed
                send_command_to_ugv02(prev_speed[0], prev_speed[1])
                print(f"{motor_speed[0]}, {motor_speed[1]}")
            except socket.timeout:
                send_command_to_ugv02(prev_speed[0], prev_speed[1])
                print(f"{prev_speed[0]}, {prev_speed[1]}")
    finally:
        sock.close()
        ser.close()

def listen_for_termination(port, terminate):
    while True:
        if receive_integer(port) == 1:
            terminate.set()
            break
