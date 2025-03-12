import os
from flask import Flask, request, jsonify
from spectrogram import generate_spectrogram
from file_converter import convert_webm_to_wav

app = Flask(__name__)

UPLOAD_FOLDER = '/app/song-storage/songs'
SPECTROGRAM_FOLDER = '/app/song-storage/spectrogram'

@app.route('/spectogramFromFile', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Create the upload directory if it does not exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    file.save(file_path)

    if request.files['file'].filename.split('.')[-1] == 'webm':
        wav_file_path = os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(file.filename)[0]}.wav")
        convert_webm_to_wav(file_path, wav_file_path)
        os.remove(file_path)
        file_path = wav_file_path

    spectrogram_path = generate_spectrogram(
        file_path,
        os.path.join(
            SPECTROGRAM_FOLDER,
            f"{os.path.splitext(file.filename)[0]}_spectrogram.png"
                    )
    )

    return jsonify({
        'message': 'Spectrogram generated',
        'spectrogram': os.path.basename(spectrogram_path)
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy", message="Service is running"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)