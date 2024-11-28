import speech_recognition as sr
from multiprocessing import Process, Queue
import time
from datetime import datetime, timedelta


def listen_for_commands(command_queue, max_duration):
    """
    Continuously listens for voice commands for a specified duration.
    Sends recognized commands to the command queue.
    """
    recognizer = sr.Recognizer()
    keywords = {
        "activate": ["start system", "system on", "activate", "begin", "wake up"],
        "deactivate": ["stop system", "system off", "deactivate", "shutdown", "sleep"],
        "alarm_off": ["alarm off", "quiet", "stop alarm"]
    }

    end_time = datetime.now() + timedelta(hours=max_duration)
    print(f"Monitoring started. Program will run until {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=1)
        print("Microphone calibrated to ambient noise. Listening for commands...")

        while datetime.now() < end_time:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Listening for commands...")
                audio = recognizer.listen(mic, timeout=10, phrase_time_limit=5)
                print("Audio input detected. Processing...")
                result = recognizer.recognize_google(audio, show_all=True)

                if result and "alternative" in result:
                    command_text = result["alternative"][0]["transcript"].lower()
                    print(f"Detected command: {command_text}")

                    for command, triggers in keywords.items():
                        if any(trigger in command_text for trigger in triggers):
                            print(f"Command recognized: {command}")
                            command_queue.put(command.upper())
                            break

            except sr.WaitTimeoutError:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Timeout: No speech detected.")
            except sr.UnknownValueError:
                print("Speech not clear. Waiting for the next input...")
            except sr.RequestError as e:
                print(f"Speech recognition service error: {e}")
            except Exception as ex:
                print(f"Unexpected error: {ex}")
    
    print("Monitoring period ended. Exiting voice recognition process.")


def control_system():
    """
    Handles the main system logic, processing commands and managing states.
    """
    command_queue = Queue()
    max_duration = 8  # Monitoring duration in hours

    print("Starting the Smart Monitoring System...")
    voice_process = Process(target=listen_for_commands, args=(command_queue, max_duration))
    voice_process.start()

    states = {
        "system_active": False,
        "alarm_active": True
    }

    try:
        while voice_process.is_alive():
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
        print("\nSystem interrupted by user. Shutting down...")
    finally:
        voice_process.terminate()
        voice_process.join()
        print("System fully stopped.")


if __name__ == '__main__':
    control_system()
