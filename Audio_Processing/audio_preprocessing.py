import numpy as np
from scipy.signal import stft

def get_spectrogram(audio, sample_rate=16000):
    f, t, Zxx = stft(audio, fs=sample_rate, nperseg=255, noverlap=124, nfft=256)
    spectrogram = np.abs(Zxx)  # Take the magnitude
    spectrogram = np.expand_dims(spectrogram, axis=-1)  # Add channel dimension
    spectrogram = np.expand_dims(spectrogram, axis=0)  # Add batch dimension
    return spectrogram
