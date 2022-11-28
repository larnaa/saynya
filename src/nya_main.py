import warnings
warnings.simplefilter('ignore')
import nussl
from pathlib import Path
import IPython
import numpy as np

input_file_path = Path(__file__).parent.parent / 'cats-meow-1.wav'

# Initialization from a File
signal1 = nussl.AudioSignal(input_file_path)
signal1.write_audio_to_file(Path(__file__).parent.parent / 'signal1.wav')


# Initialization from a numpy array
sample_rate = 44100  # Hz
dt = 1.0 / sample_rate
dur = 2.0  # seconds
freq = 440  # Hz
x = np.arange(0.0, dur, dt)
x = np.sin(2 * np.pi * freq * x)


signal2 = nussl.AudioSignal(
    audio_data_array=x, sample_rate=sample_rate)
signal2.write_audio_to_file(Path(__file__).parent.parent / 'signal2.wav')


signal1.to_mono(overwrite=True)
signal1.truncate_seconds(signal2.signal_duration)

signal3 = signal1 + signal2
signal3.peak_normalize()
signal3.write_audio_to_file(Path(__file__).parent.parent / 'signal3.wav')
