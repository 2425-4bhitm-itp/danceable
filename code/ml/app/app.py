import json
import os

import joblib
import numpy as np
from flask import Flask, request, jsonify

from config.paths import SCALER_PATH
from config.paths import SNIPPETS_DIR, SONGS_DIR, LABELS_PATH
from features.audio_dataset_creator import AudioDatasetCreator
from features.audio_feature_extractor import AudioFeatureExtractor
from training.model import train, classify_audio, load_model
from utilities import shorten, file_converter, sort

flask_app = Flask(__name__)

extractor = AudioFeatureExtractor()
dataset_creator = AudioDatasetCreator(extractor)

is_processing = False

scaler = None


def get_scaler():
    global scaler
    if scaler is None:
        scaler = joblib.load(SCALER_PATH)
    return scaler["scaler"]


@flask_app.route("/process_all_audio", methods=["POST"])
def process_all_audio():
    global is_processing
    is_processing = True

    count = 0
    label_count = len(os.listdir(SNIPPETS_DIR))

    for label in os.listdir(SNIPPETS_DIR):
        single_SONGS_DIR = os.path.join(SNIPPETS_DIR, label)

        print(f"Processing folder {single_SONGS_DIR} ({count + 1}/{label_count}):")
        dataset_creator.process_folder(single_SONGS_DIR, label)
        count += 1

    is_processing = False
    return jsonify({"message": "Processing completed."}), 200


@flask_app.route("/processing", methods=["GET"])
def is_processing():
    return jsonify({"processing": is_processing}), 200


@flask_app.route("/upload_wav_file", methods=["POST"])
def upload_wav_file():
    data = request.get_json()
    file_path = data["file_path"]
    label = data["label"]
    dataset_creator.upload_single_file(file_path, label)
    return jsonify({"message": "File uploaded."}), 200


@flask_app.route("/features", methods=["POST"])
def extract_features():
    data = request.get_json(silent=True)
    file_path = request.args.get("file_path") or (data and data.get("file_path"))

    if not file_path:
        return jsonify({"error": "Missing 'file_path' in request query parameters or JSON body"}), 400

    features = extractor.extract_features_from_file(file_path)
    vector = np.array(list(features.values()), dtype=np.float32).reshape(1, -1)
    scaler = get_scaler()
    vector = scaler.transform(vector)

    return jsonify(vector.tolist()), 200


@flask_app.route("/train", methods=["GET"])
def train_model():
    accuracy, val_accuracy = train()

    return jsonify({
        "message": "Training completed.",
        "accuracy": accuracy,
        "val_accuracy": val_accuracy
    }), 200


@flask_app.route("/classify_audio", methods=["POST"])
def classify_audio_api():
    file_path = request.args.get('file_path')

    if not file_path:
        return jsonify({"error": "Missing 'file_path' in request query parameters"}), 400

    print(file_path)
    predictions = classify_audio(file_path, extractor)
    return jsonify(predictions), 200


@flask_app.route("/classify_webm_audio", methods=["POST"])
def upload_webm_file():
    data = request.get_json()
    file_path = data["file_path"]

    wav_file = file_path.replace(".webm", ".wav")
    wav_file_path = file_converter.convert_webm_to_wav(file_path, wav_file)

    prediction = classify_audio(wav_file_path, extractor)
    return jsonify(prediction), 200


@flask_app.route("/classify_caf_audio", methods=["POST"])
def upload_caf_file():
    data = request.get_json(silent=True)
    if not data or "file_path" not in data:
        return jsonify({"error": "Invalid or missing 'file_path' in request body"}), 400

    file_path = data["file_path"]
    wav_file = file_path.replace(".caf", ".wav")
    wav_file_path = file_converter.convert_caf_to_wav(file_path, wav_file)

    prediction = classify_audio(wav_file_path, extractor)
    return jsonify(prediction), 200


@flask_app.route("/classify_audio_all", methods=["POST"])
def classify_audio_all_api():
    data = request.get_json(silent=True)
    if not data or "file_path" not in data:
        return jsonify({"error": "Missing 'file_path' in request body"}), 400

    file_path = data["file_path"]

    if file_path.endswith(".webm"):
        file_path = file_converter.convert_webm_to_wav(file_path, file_path.replace(".webm", ".wav"))
    elif file_path.endswith(".caf"):
        file_path = file_converter.convert_caf_to_wav(file_path, file_path.replace(".caf", ".wav"))

    global model, scaler
    if model is None or scaler is None:
        load_model()

    features = extractor.extract_features_from_file(file_path)
    vector = np.array(list(features.values()), dtype=np.float32).reshape(1, -1)
    vector = scaler["scaler"].transform(vector)

    with open(LABELS_PATH) as f:
        labels = json.load(f)

    probs = model.predict(vector, verbose=0)[0]

    # Build response for all classes
    all_predictions = [
        {"danceName": label, "confidence": float(f"{prob * 100:.2f}")}
        for label, prob in zip(labels, probs)
    ]

    return jsonify({"predictions": all_predictions}), 200


@flask_app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy", message="Service is running"), 200


@flask_app.route('/split_and_sort', methods=['POST'])
def split_and_sort():
    segment_length = request.get_json()["segment_length"]
    split_files()
    sort.sort_and_delete_wav_files(SNIPPETS_DIR)
    return jsonify({"message": "Shortening and sorting completed"}), 200


@flask_app.route('/split_files', methods=['POST'])
def split_files():
    segment_length = request.get_json()["segment_length"]
    shorten.split_wav_files(SONGS_DIR, SNIPPETS_DIR, segment_length)
    return jsonify({"message": "Shortening completed"}), 200


if __name__ == '__main__':
    load_model()
    flask_app.run(host='0.0.0.0', port=5001, debug=True)
