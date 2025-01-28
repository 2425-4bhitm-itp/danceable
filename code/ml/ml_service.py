from flask import Flask, request, jsonify
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import warnings
import os

app = Flask(__name__)

@app.route('/spectogramFromFile', methods=['POST'])
def spectogramFromFile():
    fileName = request.json['fileName']

    # Force correct paths to avoid issues with incorrect input
    input_path = os.path.join('/app/song-storage/songs', os.path.basename(fileName))

    file_name_without_ext = os.path.splitext(os.path.basename(fileName))[0]
    output_path = os.path.join('/app/song-storage/spectrogram', file_name_without_ext + '_spectogram')

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File {input_path} not found!")

    generate_spectrogram(input_path, output_path)

    return jsonify({'result': 'generated successfully'}), 200

def generate_spectrogram(wav_filename, output_filename='spectrogram'):
    # Ensure the /app/song-storage/spectrogram directory exists
    os.makedirs('/app/song-storage/spectrogram', exist_ok=True)

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
    plt.savefig(output_filename)
    plt.close()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy", message="Service is running"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
