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
    generate_spectrogram(fileName, fileName + '_spectogram')

    return jsonify({'result': 'generated successfully'}), 200

def generate_spectrogram(wav_filename, output_filename='spectrogram'):
    # Ensure the /spectograms directory exists
    os.makedirs('spectograms', exist_ok=True)

    # Prepend the /spectograms directory to the output filename
    output_filename = os.path.join('spectograms', output_filename)

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
