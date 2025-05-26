from audio_feature_extractor import AudioFeatureExtractor
from audio_dataset_creator import AudioDatasetCreator
from model import train, classify_audio, load_model
import file_converter
import os
from flask import Flask, request, jsonify
import shorten
import sort

app = Flask(__name__)

extractor = AudioFeatureExtractor()
dataset_creator = AudioDatasetCreator(extractor)
folder_path = "/app/song-storage/songs"
snippets_path = "/app/song-storage/songs/snippets"

is_processing = False

@app.route("/process_all_audio", methods=["POST"])
def process_all_audio():
    global is_processing
    is_processing = True

    open("/app/song-storage/features.csv", "w").close()
    count = 0
    label_count = len(os.listdir(snippets_path))

    for label in os.listdir(snippets_path):
        single_folder_path = os.path.join(snippets_path, label)

        print(f"Processing folder {single_folder_path} ({count+1}/{label_count}):")
        dataset_creator.process_folder(single_folder_path, label)
        count += 1

    is_processing = False
    return jsonify({"message": "Processing completed."}), 200

@app.route("/processing", methods=["GET"])
def is_processing():
    return jsonify({"processing": is_processing}), 200

@app.route("/upload_wav_file", methods=["POST"])
def upload_wav_file():
    data = request.get_json()
    file_path = data["file_path"]
    label = data["label"]
    dataset_creator.upload_single_file(file_path, label)
    return jsonify({"message": "File uploaded."}), 200

@app.route("/features", methods=["POST"])
def extract_features():
    data = request.get_json(silent=True)
    file_path = request.args.get("file_path") or (data and data.get("file_path"))

    if not file_path:
        return jsonify({"error": "Missing 'file_path' in request query parameters or JSON body"}), 400

    features = extractor.extract_features_from_file(file_path)
    features_serialized = {key: value.tolist() for key, value in features.items()}
    return jsonify({"features": features_serialized}), 200

@app.route("/train", methods=["GET"])
def train_model():
    accuracy, val_accuracy = train()

    return jsonify({
        "message": "Training completed.",
        "accuracy": accuracy,
        "val_accuracy": val_accuracy
    }), 200

@app.route("/classify_audio", methods=["POST"])
def classify_audio_api():
    file_path = request.args.get('file_path')

    if not file_path:
        return jsonify({"error": "Missing 'file_path' in request query parameters"}), 400

    print(file_path)
    predictions = classify_audio(file_path, extractor)
    return jsonify(predictions), 200


@app.route("/classify_webm_audio", methods=["POST"])
def upload_webm_file():
    data = request.get_json()
    file_path = data["file_path"]

    wav_file = file_path.replace(".webm", ".wav")
    wav_file_path = file_converter.convert_webm_to_wav(file_path, wav_file)

    prediction = classify_audio(wav_file_path, extractor)
    return jsonify({"prediction": prediction}), 200

@app.route("/classify_caf_audio", methods=["POST"])
def upload_caf_file():
    data = request.get_json(silent=True)
    if not data or "file_path" not in data:
        return jsonify({"error": "Invalid or missing 'file_path' in request body"}), 400

    file_path = data["file_path"]
    wav_file = file_path.replace(".caf", ".wav")
    wav_file_path = file_converter.convert_caf_to_wav(file_path, wav_file)

    prediction = classify_audio(wav_file_path, extractor)
    return jsonify({"prediction": prediction}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy", message="Service is running"), 200

@app.route('/split_and_sort', methods=['POST'])
def split_and_sort():
    segment_length = request.get_json()["segment_length"]
    split_files()
    sort.sort_and_delete_wav_files(snippets_path)
    return jsonify({"message": "Shortening and sorting completed"}), 200

@app.route('/split_files', methods=['POST'])
def split_files():
    segment_length = request.get_json()["segment_length"]
    shorten.split_wav_files(folder_path, snippets_path, segment_length)
    return jsonify({"message": "Shortening completed"}), 200

if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=5001, debug=True)