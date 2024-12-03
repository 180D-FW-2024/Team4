import socket
import time
import speech_recognition as sr
import threading

# Define the UDP IP and port
UDP_IP = "192.168.1.16"  # Replace with the receiver's IP address
UDP_PORT = 5200

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Keywords for activation and deactivation
keywords = {
    "activate": ["start system", "system on", "activate", "begin", "wake up"],
    "deactivate": ["stop system", "system off", "deactivate", "shutdown", "sleep"]
}

# Initial state
boolean_value = True

def listen_for_commands():
    """
    Continuously listen for voice commands and update the system state.
    """
    global boolean_value

    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=1)
        print("Microphone calibrated. Listening for commands...")

        while True:
            try:
                print("Listening...")
                audio = recognizer.listen(mic, timeout=10, phrase_time_limit=5)
                print("Audio detected, processing...")

                # Recognize speech using Sphinx (offline)
                command_text = recognizer.recognize_sphinx(audio).lower()
                print(f"Recognized command: {command_text}")

                # Update the boolean_value based on recognized commands
                for command, triggers in keywords.items():
                    if any(trigger in command_text for trigger in triggers):
                        if command == "activate":
                            boolean_value = True
                            print("System activated.")
                        elif command == "deactivate":
                            boolean_value = False
                            print("System deactivated.")
                        break

            except sr.UnknownValueError:
                print("Could not understand the audio. Waiting for the next input...")
            except sr.RequestError as e:
                print(f"Speech recognition service error: {e}")
            except sr.WaitTimeoutError:
                print("Timeout: No speech detected. Retrying...")

# Start the listener thread
listener_thread = threading.Thread(target=listen_for_commands, daemon=True)
listener_thread.start()

try:
    while True:
        # Convert boolean to "1" (True) or "0" (False)
        message = "1" if boolean_value else "0"

        # Send the message over UDP
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
        print(f"Sent: {boolean_value}")

        # Pause for 1 second before sending the next message
        time.sleep(1)

except KeyboardInterrupt:
    print("Sender stopped.")

finally:
    sock.close()
