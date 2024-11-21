import threading
from cam import send_frames_to_udp  # Import from cam.py
from receive_data import receive_motor_speed, listen_for_termination  # Import from receive_data.py

terminate = threading.Event()

def main():
    control_computer_address = '192.168.4.15'

    termination_thread = threading.Thread(target=listen_for_termination, args=(8889, terminate))
    termination_thread.start()

    motor_speed_thread = threading.Thread(target=receive_motor_speed, args=(8890, terminate))
    motor_speed_thread.start()

    camera_thread = threading.Thread(target=send_frames_to_udp, args=((control_computer_address, 8888), terminate))
    camera_thread.start()

    termination_thread.join()
    motor_speed_thread.join()
    camera_thread.join()

if __name__ == '__main__':
    main()
