import speech_recognition as sr
from multiprocessing import Process, Queue
import time

def listen_for_commands(command_queue):
    """
    Continuously listens for voice commands and sends them to the command queue.
    """
    recognizer = sr.Recognizer()
    keywords = {
        "activate": ["start system", "system on", "activate", "begin", "wake up"],
        "deactivate": ["stop system", "system off", "deactivate", "shutdown", "sleep"],
        "alarm_off": ["alarm off", "quiet", "stop alarm"]
    }

    time.sleep(1)  # Give the microphone some time to initialize
    print("Initializing voice recognition...")
    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=1)
        print("Voice recognition ready. Speak a command!")

        while True:
            try:
                print("Listening for commands...")
                audio = recognizer.listen(mic, timeout=4, phrase_time_limit=2)
                result = recognizer.recognize_google(audio, show_all=True)

                if result and "alternative" in result:
                    command_text = result["alternative"][0]["transcript"].lower()
                    print(f"Detected command: {command_text}")

                    for command, triggers in keywords.items():
                        if any(trigger in command_text for trigger in triggers):
                            command_queue.put(command.upper())
                            break

            except sr.UnknownValueError:
                print("Could not understand the audio. Please repeat.")
            except sr.RequestError as e:
                print(f"Speech recognition service error: {e}")
            except Exception as ex:
                print(f"Unexpected error: {ex}")
                break


def control_system():
    """
    Handles the main system logic, processing commands and managing states.
    """
    command_queue = Queue()
    voice_process = Process(target=listen_for_commands, args=(command_queue,))
    voice_process.start()

    states = {
        "system_active": False,
        "alarm_active": True
    }

    print("Smart Monitoring System Started")
    print("Waiting for commands...")

    try:
        while True:
            if not command_queue.empty():
                command = command_queue.get()

                if command == "ACTIVATE":
                    if not states["system_active"]:
                        states["system_active"] = True
                        print("The system is now active!")
                    else:
                        print("System is already active.")

                elif command == "DEACTIVATE":
                    if states["system_active"]:
                        states["system_active"] = False
                        print("The system has been deactivated.")
                    else:
                        print("System is already inactive.")

                elif command == "ALARM_OFF":
                    if states["alarm_active"]:
                        states["alarm_active"] = False
                        print("The alarm has been deactivated.")
                    else:
                        print("The alarm is already off.")

            # Perform active system tasks
            if states["system_active"]:
                print("System is currently active and monitoring...")
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nSystem interrupted. Shutting down...")
    finally:
        voice_process.terminate()
        voice_process.join()
        print("System fully stopped.")

if __name__ == "__main__":
    print("Main function is being executed...")
    control_system()  # Call your main function here