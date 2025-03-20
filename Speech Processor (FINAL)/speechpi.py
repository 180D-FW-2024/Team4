import os
import re
import time
import io
import subprocess
import tempfile
import asyncio
import threading
import requests
import speech_recognition as sr
import socket
from edge_tts import Communicate
from groq import Groq

# LangChain + Groq LLM imports
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser

###############################################################################
# 1) TEXT-TO-SPEECH (TTS) UTILITIES
###############################################################################

async def synthesize_and_play(text: str):
    temp_mp3_path = None
    temp_wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
            temp_mp3_path = tmp_mp3.name

        communicate = Communicate(text, voice="en-US-GuyNeural")
        await communicate.save(temp_mp3_path)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            temp_wav_path = tmp_wav.name

        subprocess.run(
            [
                "ffmpeg", "-i", temp_mp3_path,
                "-af", "volume=2.0",  # Amplify volume
                "-y",                # Overwrite output
                temp_wav_path
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        subprocess.run(
            ["aplay", "-D", "plughw:3,0", temp_wav_path],
            check=True
        )

    except subprocess.CalledProcessError as e:
        print(f"Process error: {e}\n{e.stderr.decode()}")
    except Exception as ex:
        print(f"Error: {ex}")
    finally:
        for path in [temp_mp3_path, temp_wav_path]:
            if path and os.path.exists(path):
                os.remove(path)

def speak(text: str):
    asyncio.run(synthesize_and_play(text))


###############################################################################
# 2) LLM SETUP: Use LangChain-Groq to interpret ON/OFF commands
###############################################################################

os.environ["GROQ_API_KEY"] = "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"

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.1
)

class CommandOutput(BaseModel):
    command: str = Field(description="The command issued by the user.")
    state: bool = Field(
        description="The state of the command; true for 'on'/activation commands, false for 'off'/deactivation commands."
    )

pydantic_parser = PydanticOutputParser(pydantic_object=CommandOutput)
fixing_parser = OutputFixingParser.from_llm(parser=pydantic_parser, llm=llm)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant. Return a JSON object with keys 'command' and 'state' only. 'state' must be true or false."
    ),
    ("user", "{input}")
])

chain = prompt | llm | fixing_parser

def interpret_command(command: str) -> bool:
    try:
        result = chain.invoke({"input": command})
        return result.state
    except Exception as e:
        print(f"Error interpreting command '{command}': {e}")
        return None


###############################################################################
# 3) AUDIO TRANSCRIPTION: Using Groq’s Distil-Whisper endpoint
###############################################################################

GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
#API_KEY_AUDIO = "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"
#API_KEY_AUDIO = "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"
API_KEY_AUDIO = "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"
#API_KEY_AUDIO = "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"
#API_KEY_AUDIO = "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"
#API_KEY_AUDIO = "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"


def send_audio_to_groq(audio):
    audio_data = audio.get_wav_data()
    audio_file = io.BytesIO(audio_data)

    headers = {
        "Authorization": f"Bearer {API_KEY_AUDIO}"
    }
    files = {
        "file": ("audio.wav", audio_file, "audio/wav")
    }
    data = {
        "model": "distil-whisper-large-v3-en",
        "response_format": "json",
        "language": "en",
        "temperature": 0.0
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, files=files, data=data)
        if response.status_code == 200:
            transcription = response.json()
            return transcription.get("text", "").lower().strip()
        else:
            print(f"Error in transcription request: {response.status_code} - {response.text}")
            return None
    except Exception as ex:
        print(f"send_audio_to_groq error: {ex}")
        return None


###############################################################################
# 4) MAIN LOGIC: Wake phrase, stop phrase, command toggling
###############################################################################

recognizer = sr.Recognizer()
boolean_value = False  # <-- CHANGED HERE: start off
watcher_activated = False

WAKE_PHRASES = [
    "hey watcher", "hey watchers", "hi watcher", "hi watchers",
    "ok watcher",  "ok watchers",  "okay watcher", "okay watchers"
]

STOP_PHRASES = ["goodbye", "good bye", "bye"]

def is_wake_phrase(text: str) -> bool:
    text_nopunct = re.sub(r"[^\w\s]", "", text.lower())
    for phrase in WAKE_PHRASES:
        if phrase in text_nopunct:
            return True
    return False

def is_stop_phrase(text: str) -> bool:
    text_nopunct = re.sub(r"[^\w\s]", "", text.lower())
    for phrase in STOP_PHRASES:
        if phrase in text_nopunct:
            return True
    return False

def listen_for_commands():
    global boolean_value, watcher_activated

    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=1)
        print("Microphone calibrated. Awaiting wake phrase...")

        while True:
            try:
                print("\nListening...")
                audio = recognizer.listen(mic, timeout=10, phrase_time_limit=5)
                print("Audio detected, transcribing...")

                command_text = send_audio_to_groq(audio)
                if not command_text:
                    continue

                print(f"Recognized speech: '{command_text}'")

                # Case 1: Not activated => check for wake phrase
                if not watcher_activated:
                    if is_wake_phrase(command_text):
                        watcher_activated = True
                        print("Watcher activated!")
                        speak("Hello, I'm listening now.")
                    else:
                        print("No wake phrase detected. Waiting...")
                    continue

                # Case 2: If activated => check for "goodbye"
                if is_stop_phrase(command_text):
                    print("Heard goodbye phrase. Deactivating watcher.")
                    watcher_activated = False
                    speak("Goodbye! I'll stop listening now.")
                    continue

                # Case 3: Process command for on/off/activate/deactivate only if it appears to be a valid system command.
                if "system" not in command_text or not (("on" in command_text) or ("off" in command_text) or ("activate" in command_text) or ("deactivate" in command_text)):
                    print("Command text does not appear to be a valid system command. Ignoring.")
                    continue

                new_state = interpret_command(command_text)
                if new_state is not None:
                    if new_state != boolean_value:
                        boolean_value = new_state
                        if boolean_value:
                            print("System state updated to: True")
                            speak("System Activated")
                        else:
                            print("System state updated to: False")
                            speak("System Deactivated")
                    else:
                        print(f"No change: system state remains {boolean_value}")

            except sr.WaitTimeoutError:
                print("Timeout: No speech detected. Retrying...")
            except sr.UnknownValueError:
                print("Could not understand the audio. Waiting for next input...")
            except sr.RequestError as e:
                print(f"Speech recognition service error: {e}")


###############################################################################
# 5) UDP SENDER LOGIC
###############################################################################

UDP_IP = "100.75.217.43"
UDP_PORT = 5200

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

###############################################################################
# 6) LAUNCH THE LISTENER THREAD & PERIODICALLY SEND STATE
###############################################################################

listener_thread = threading.Thread(target=listen_for_commands, daemon=True)
listener_thread.start()

try:
    while True:
        print(f"Current system state: {boolean_value} | Watcher Activated: {watcher_activated}")

        # Convert bool -> "1" or "0"
        message = "1" if boolean_value else "0"

        try:
            sent_bytes = sock.sendto(message.encode('utf-8'), (UDP_IP, UDP_PORT))
            print(f"Sent {sent_bytes} bytes -> {UDP_IP}:{UDP_PORT}")
        except Exception as e:
            print(f"UDP send failed: {e}")

        time.sleep(2)

except KeyboardInterrupt:
    print("Terminated by user.")
finally:
    sock.close()
