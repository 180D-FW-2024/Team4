import numpy as np
from tflite_runtime.interpreter import Interpreter
from audio_preprocessing import get_spectrogram
import pyaudio

# Load the TensorFlow Lite model
interpreter = Interpreter('simple_audio_model_numpy.tflite')
interpreter.allocate_tensors()

# Get input and output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

commands = ['go', 'down', 'up', 'stop', 'yes', 'left', 'right', 'no']

# Real-time audio capture
def record_audio(duration=1, rate=16000, chunk_size=1024):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk_size)

    frames = []
    for _ in range(0, int(rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(np.frombuffer(data, dtype=np.int16))

    stream.stop_stream()
    stream.close()
    p.terminate()
    return np.hstack(frames)

# Inference on live audio
def run_inference():
    print("Listening...")
    audio = record_audio(duration=1)
    spectrogram = get_spectrogram(audio)
    
    interpreter.set_tensor(input_details[0]['index'], spectrogram.astype(np.float32))
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(output_details[0]['index'])
    command_index = np.argmax(output_data)
    print(f"Recognized command: {commands[command_index].upper()}")

if __name__ == "__main__":
    while True:
        run_inference()
