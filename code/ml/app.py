from flask import Flask, request, jsonify
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import warnings
import os
import spectrogram

app = Flask(__name__)

@app.route('/spectogramFromFile', methods=['POST'])
def spectogramFromFile():
    fileName = request.json['fileName']

    # Force correct paths to avoid issues with incorrect input
    input_path = os.path.join('/app/song-storage/songs', os.path.basename(fileName))

    file_name_without_ext = os.path.splitext(os.path.basename(fileName))[0]
    output_path = os.path.join('/app/song-storage/spectrogram', file_name_without_ext + '_spectogram.png')

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File {input_path} not found!")

    spectrogram.generate_spectrogram(input_path, output_path)

    return jsonify({'result': 'generated successfully', 'imagePath': output_path}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy", message="Service is running"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
