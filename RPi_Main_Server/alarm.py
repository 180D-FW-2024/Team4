import os

audio_file = "chicken.wav"

def ring_alarm(audio_file=audio_file):
    os.system(f"aplay -D plughw:3,0 -f S16_LE -r 44100 {audio_file}")