import speech_recognition as sr
import time
from datetime import datetime, timedelta

def process_voice_input(audio_data, recognizer):
    """
    Processes audio data to extract recognized text using PocketSphinx.
    """
    try:
        return recognizer.recognize_sphinx(audio_data)
    except sr.UnknownValueError:
        print("Could not understand the audio. Waiting for the next input...")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")
        return None

def listen_for_commands(max_duration, states):
    """
    Continuously listens for voice commands for a specified duration.
    Updates system states based on recognized commands.
    """
    recognizer = sr.Recognizer()
    keywords = {
        "activate": ["start system", "system on", "activate", "begin", "began", "wake up", "wakeup"],
        "deactivate": ["stop system", "system off", "deactivate", "shutdown","shotdown" "sleep", "slept"],
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

                # Process the audio input
                result = process_voice_input(audio, recognizer)

                if result:
                    command_text = result.lower()
                    print(f"Detected command: {command_text}")

                    for command, triggers in keywords.items():
                        if any(trigger in command_text for trigger in triggers):
                            handle_command(command, states)
                            break

            except sr.WaitTimeoutError:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Timeout: No speech detected.")
            except Exception as ex:
                print(f"Unexpected error: {ex}")
    
    print("Monitoring period ended. Exiting voice recognition process.")

def handle_command(command, states):
    """
    Updates system states based on the recognized command.
    """
    if command == "activate":
        if not states["system_active"]:
            states["system_active"] = True
            print("The system is now active!")
        else:
            print("System is already active.")
    elif command == "deactivate":
        if states["system_active"]:
            states["system_active"] = False
            print("The system has been deactivated.")
        else:
            print("System is already inactive.")
    elif command == "alarm_off":
        if states["alarm_active"]:
            states["alarm_active"] = False
            print("The alarm has been deactivated.")
        else:
            print("The alarm is already off.")

def control_system():
    """
    Handles the main system logic and initiates voice command listening.
    """
    max_duration = 8  # Monitoring duration in hours
    states = {
        "system_active": False,
        "alarm_active": True
    }

    print("Starting the Smart Monitoring System...")
    listen_for_commands(max_duration, states)

    print("System monitoring completed.")

if __name__ == '__main__':
    control_system()