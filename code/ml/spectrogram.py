import warnings
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import os

def generate_spectrogram(wav_filename, output_filename):
    print(wav_filename)
    dir_name = os.path.basename(os.path.dirname(wav_filename))

    output_dir = os.path.join('/app/song-storage/spectrogram', dir_name)
    os.makedirs(output_dir, exist_ok=True)

    if output_filename[-4:] != '.png':
        output_filename += '.png'

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        sample_rate, data = wavfile.read(wav_filename)

    # If stereo, take only one channel
    if len(data.shape) > 1:
        data = data[:, 0]

    frequencies, times, Sxx = spectrogram(data, fs=sample_rate, nperseg=8192, noverlap=4096, window='hann')

    # Normalize
    Sxx[Sxx == 0] = np.finfo(float).eps
    Sxx = 10 * np.log10(Sxx)
    Sxx -= Sxx.min()
    Sxx /= Sxx.max()

    # Ensure no NaN or Inf in Sxx
    Sxx[np.isnan(Sxx)] = 0
    Sxx[np.isinf(Sxx)] = 0

    fig, ax = plt.subplots(figsize=(10.24, 5.12), dpi=300)
    ax.pcolormesh(times, frequencies, Sxx, shading='gouraud', cmap='viridis')
    ax.axis('off')

    plt.tight_layout()
    output_filename = os.path.join(output_dir, os.path.basename(wav_filename) + '_spectrogram.png')
    plt.savefig(output_filename, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

    return output_filename