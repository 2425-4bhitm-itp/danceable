import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import warnings
import os

def generate_spectrogram(wav_filename, output_filename='spectrogram'):
    # Ensure the /app/song-storage/spectrogram directory exists
    dir_name = os.path.basename(os.path.dirname(wav_filename))  # Get the directory name of the song
    output_dir = os.path.join('/app/song-storage/spectrogram', dir_name)
    os.makedirs(output_dir, exist_ok=True)

    if output_filename[-4:] != '.png':
        output_filename += '.png'

    # Read the WAV file with warning suppression
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        sample_rate, data = wavfile.read(wav_filename)

    # If stereo, take only one channel
    if len(data.shape) > 1:
        data = data[:, 0]

    # Generate the spectrogram with higher resolution
    nperseg = 4096  # Increase FFT size for better frequency resolution
    noverlap = nperseg // 2  # 50% overlap for better time resolution
    window = 'hann'  # Use a Hanning window

    frequencies, times, Sxx = spectrogram(data, fs=sample_rate, nperseg=nperseg, noverlap=noverlap, window=window)

    # Avoid log of zero issues
    Sxx[Sxx == 0] = np.finfo(float).eps

    # Normalize the spectrogram
    Sxx = 10 * np.log10(Sxx)
    Sxx -= Sxx.min()  # Shift to start from zero
    Sxx /= Sxx.max()  # Normalize to 0-1 range

    # Cap the frequency to 20kHz
    max_frequency = 20000
    frequencies = frequencies[frequencies <= max_frequency]
    Sxx = Sxx[:len(frequencies), :]

    # Plot the spectrogram
    plt.figure(figsize=(12, 8))
    plt.pcolormesh(times, frequencies, Sxx, shading='gouraud')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.title('Spectrogram of ' + wav_filename)
    plt.colorbar(label='Normalized Power')

    # Save the spectrogram to the new folder
    output_file = os.path.join(output_dir, os.path.basename(wav_filename) + '_spectrogram.png')
    plt.savefig(output_file)
    plt.close()