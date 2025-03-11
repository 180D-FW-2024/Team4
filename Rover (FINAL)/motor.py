import serial
import json


class Motor:
    def __init__(self):
        try:
            self.ser = serial.Serial('/dev/serial0', baudrate=1000000, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening the serial port: {e}")
            exit()


    def drive_ugv02_motor(self, left_power, right_power):
        # -255 to 255 range
        left_power_scaled = int(left_power * 255)
        right_power_scaled = int(right_power * 255)
        left_power_scaled = max(min(left_power_scaled, 255), -255)
        right_power_scaled = max(min(right_power_scaled, 255), -255)

        command = {
            "T": 1,  # Movement control command type
            "L": left_power_scaled,
            "R": right_power_scaled
        }

        command_json = json.dumps(command) + '\n'
        try:
            self.ser.write(command_json.encode('utf-8'))
        except Exception as e:
            print(f"Error sending command to UGV02: {e}")
    
    def forward(self):
        self.drive_ugv02_motor(255, 255)
    
    def backwards(self):
        self.drive_ugv02_motor(-255, -255)
    
    def right(self):
        self.drive_ugv02_motor(255, -255)
    
    def left(self):
        self.drive_ugv02_motor(-255, 255)
    
    def stop(self):
        self.drive_ugv02_motor(0, 0)