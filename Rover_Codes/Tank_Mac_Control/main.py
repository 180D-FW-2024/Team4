import cv2
import numpy as np
import socket
import pygame
import logging

from image_processing import *
from motor_control import *
from data_to_cboard import *

logging.basicConfig(level=logging.DEBUG)

cboard_address = '192.168.1.96'

# Initialize pygame and the joystick if available
pygame.init()
try:
    pygame.joystick.Joystick(0).init()
except pygame.error:
    pass

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the listening address and port
server_address = ('0.0.0.0', 8888)
sock.bind(server_address)

def main():
    visual_ctrl = "Normal"
    turn_on_obj = False
    movement = "Neutral"
    motor_speed = [0.0, 0.0] # [left, right]
    max_speed = 100.0

    # display_image("")  # Display intro frame, assuming this function is defined correctly

    try:
        while True:
            try:
                packet, _ = sock.recvfrom(65535) # Receive packet
                # logging.debug("Packet received")

                frame_data = np.frombuffer(packet, np.uint8)
                frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)

                if frame is not None:
                    # logging.debug(f"Frame shape: {frame.shape}")
                    # Process pygame events
                    pygame.event.pump()
                    keys = pygame.key.get_pressed()

                    movement, motor_speed, max_speed = movement_process(keys, movement, motor_speed) # Update movement based on input

                    # Update visual control and object detection toggle based on input
                    visual_ctrl, turn_on_obj = input_control(keys, visual_ctrl, turn_on_obj)

                    # Process the frame with selected visual effects and object detection
                    processed_frame = image_process(frame, visual_ctrl, turn_on_obj, movement, motor_speed, max_speed)
                    cv2.imshow("RC Visual", processed_frame)

                    # Send motor speed data to the control board
                    send_motor_speed((cboard_address, 8890), motor_speed)

                    if keys[pygame.K_q]:  # Exit loop if 'q' is pressed
                        break

            except socket.timeout:
                logging.debug("Socket timeout, no packet received")

            if cv2.waitKey(1) & 0xFF == ord('q'): # Also allows breaking with 'q' from the CV2 window
                break

    finally:
        # Cleanup
        # send_integer_to_rpi(sock, 1, (cboard_address, 8889)) # Send termination signal
        sock.close()
        cv2.destroyAllWindows()
        pygame.quit()

if __name__ == "__main__":
    main()
