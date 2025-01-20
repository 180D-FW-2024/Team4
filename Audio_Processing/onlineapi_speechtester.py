import time
import speech_recognition as sr
import threading
import requests
from groq import Groq
import io

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"  # Transcriptions endpoint
API_KEY = "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"  # Your Groq API Key

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Keywords for activation and deactivation
keywords = {
    "activate": ["start system", "system on", "activate", "begin", "wake up"],
    "deactivate": ["stop system", "system off", "deactivate", "shutdown", "sleep"]
}

# Initial system state
boolean_value = True

# Function to send audio to Groq API for transcription
def send_audio_to_groq(audio):
    """Send the captured audio to the Groq API for speech-to-text processing."""
    # Convert the audio to WAV format (if it's not already in WAV)
    audio_data = audio.get_wav_data()  # Convert audio to WAV format
    audio_file = io.BytesIO(audio_data)  # Create an in-memory file-like object

    # Set up headers and data for the request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Send the audio to the Groq API for transcription
    files = {'file': ('audio.wav', audio_file, 'audio/wav')}
    
    # Specify the model as distil-whisper-large-v3-en
    response = requests.post(GROQ_API_URL, headers=headers, files=files, data={
        'model': 'distil-whisper-large-v3-en',  # Specify the model to use
        'response_format': 'json',  # Optional, return results in JSON
        'language': 'en',  # Specify language (for English)
        'temperature': 0.0  # Optional, for controlling output style
    })

    if response.status_code == 200:
        transcription = response.json()
        return transcription.get("text", "").lower()  # Extract transcribed text from response
    else:
        print(f"Error in transcription request: {response.status_code} - {response.text}")
        return None

def listen_for_commands():
    """Continuously listen for voice commands and update the system state."""
    global boolean_value

    with sr.Microphone() as mic:
        # Adjust the recognizer sensitivity to ambient noise
        recognizer.adjust_for_ambient_noise(mic, duration=1)
        print("Microphone calibrated. Listening for commands...")

        while True:
            try:
                print("Listening...")
                # Capture audio from the microphone
                audio = recognizer.listen(mic, timeout=10, phrase_time_limit=5)
                print("Audio detected, processing...")

                # Send the audio to Groq for speech recognition
                command_text = send_audio_to_groq(audio)
                
                if command_text:
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
        # Simply print the current boolean_value to confirm toggling
        print(f"Current system state: {boolean_value}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Terminated by user.")
