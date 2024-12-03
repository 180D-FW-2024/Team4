import subprocess

sound_file = "mixkit-classic-alarm-995.wav"

def ring_alarm(sound_file=sound_file):
    """
    Rings an alarm by playing a sound file using `aplay`.

    :param sound_file: Path to the .wav file to play.
    """
    try:
        # Play the sound using `aplay` and specify the USB speaker (hw:3,0)
        subprocess.run(["aplay", "-D", "hw:3,0", sound_file], check=True)
        print("Alarm played successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error playing sound: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
