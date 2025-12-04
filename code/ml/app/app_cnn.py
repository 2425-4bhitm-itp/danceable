import os
import json
import uuid
from pathlib import Path

import numpy as np
import concurrent.futures

import pandas as pd
from flask import Flask, request, jsonify, send_from_directory, Response

from config.paths import (
    SNIPPETS_DIR,
    SONGS_DIR,
    LABELS_PATH,
    CNN_MODEL_PATH,
    CNN_TRAIN_DATA_DIR, CNN_OUTPUT_CSV, SCALER_PATH, CNN_LABELS_PATH, BASE_MODEL_DIR
)

from features.feature_extractor_cnn import AudioFeatureExtractorCNN
from features.dataset_creator_cnn import AudioDatasetCreatorCNN
from training.model_cnn import (
    build_cnn,
    train_model,
    classify_audio,
    load_model
)

from utilities import shorten, sort, file_converter


flask_app = Flask(__name__)

extractor = AudioFeatureExtractorCNN()
dataset_creator = AudioDatasetCreatorCNN(extractor)

cnn_model = None
processing_flag = False


def convert_to_wav_if_needed(file_path):
    if file_path.endswith(".wav"):
        return file_path
    if file_path.endswith(".webm"):
        return file_converter.convert_webm_to_wav(file_path, file_path.replace(".webm", ".wav"))
    if file_path.endswith(".caf"):
        return file_converter.convert_caf_to_wav(file_path, file_path.replace(".caf", ".wav"))
    return file_path


def process_single_audio(path, label):
    wav_path = convert_to_wav_if_needed(path)
    tensor = extractor.wav_to_spectrogram_tensor(wav_path)

    # Generate unique filename
    window_id = str(uuid.uuid4())
    save_path = dataset_creator.output_dir / f"{window_id}.npz"

    # Save the tensor
    np.savez(save_path, input=tensor, label=label)

    # Update CSV so we can track processed files
    row = {
        "window_id": window_id,
        "filename": os.path.basename(wav_path),
        "label": label,
        "npy_path": str(save_path)
    }
    dataset_creator.save_csv([row])

@flask_app.route("/process_all_audio", methods=["POST"])
def process_all_audio():
    global processing_flag
    processing_flag = True

    labels = os.listdir(SNIPPETS_DIR)
    print(f"Starting audio processing for {len(labels)} labels")

    # Load already processed files from the dataset creator
    processed_files = dataset_creator.load_existing()

    # Collect tasks first so we can show progress
    tasks = []
    skipped = 0
    for label in labels:
        folder = os.path.join(SNIPPETS_DIR, label)
        wav_files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if f.lower().endswith((".wav", ".webm", ".caf"))]
        for file_path in wav_files:
            if str(file_path) in processed_files:
                skipped += 1
                continue
            tasks.append((file_path, label))

    total = len(tasks)
    if total == 0:
        print(f"No new files to process (skipped {skipped} already processed).")
        processing_flag = False
        return jsonify({"message": "No new files to process", "skipped": skipped}), 200

    print(f"Processing {total} files (skipped {skipped} already processed)")

    def process_file(file_path, label):
        try:
            process_single_audio(file_path, label)
        except Exception as e:
            # re-raise so the as_completed loop can report it
            raise

    processed_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_task = {executor.submit(process_file, fp, lbl): (fp, lbl) for fp, lbl in tasks}

        for future in concurrent.futures.as_completed(future_to_task):
            fp, lbl = future_to_task[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing {fp}: {e}")
            processed_count += 1
            pct = processed_count / total
            print(f"Progress: {processed_count}/{total} ({pct:.1%}) - last: {os.path.basename(fp)}")

    processing_flag = False
    print("Audio processing completed for all files")
    return jsonify({"message": "Processing completed", "total": total, "skipped": skipped}), 200


@flask_app.route("/upload_audio", methods=["POST"])
def upload_audio():
    data = request.get_json()
    process_single_audio(data["file_path"], data["label"])
    return jsonify({"message": "File processed"}), 200


@flask_app.route("/train", methods=["POST"])
def train():
    data = request.get_json()
    disabled_labels = data.get("disabled_labels", [])
    test_size = data.get("test_size", 0.2)
    batch_size = data.get("batch_size", 512)
    epochs = data.get("epochs", 100)

    result = train_model(
        disabled_labels=disabled_labels,
        batch_size=batch_size,
        epochs=epochs,
        test_size=test_size
    )
    accuracy = result["accuracy"]
    val_accuracy = max(result["history"]["val_accuracy"])

    return jsonify({
        "message": "Training completed",
        "accuracy": accuracy,
        "val_accuracy": val_accuracy
    }), 200

@flask_app.route("/evaluate", methods=["POST"])
def evaluate():
    from training.model_evaluator import DanceModelEvaluator

    data = request.get_json()
    disabled_labels = data.get("disabled_labels", [])
    test_size = data.get("test_size", 0.2)

    # Train or reload model
    result = train_model(disabled_labels=disabled_labels, test_size=test_size)

    # Save processed arrays
    np.savez(os.path.join(BASE_MODEL_DIR, "train_data.npz"), X=result["X_train"].to_numpy(), y=np.array(result["y_train"]))
    np.savez(os.path.join(BASE_MODEL_DIR, "val_data.npz"), X=result["X_val"].to_numpy(), y=np.array(result["y_val"]))
    np.savez(os.path.join(BASE_MODEL_DIR, "test_data.npz"), X=result["X_test"].to_numpy(), y=np.array(result["y_test"]))

    evaluator = DanceModelEvaluator(
        model_path=CNN_MODEL_PATH,
        labels_path=CNN_LABELS_PATH
    )

    evaluator.load_resources()

    datasets = evaluator.load_preprocessed_data()
    for set_name in ["train", "val", "test"]:
        X, y = datasets[set_name]
        evaluator.evaluate_from_arrays_cnn(X, y, set_name=set_name)

    accuracy = result["accuracy"]
    val_accuracy = max(result["history"]["val_accuracy"])

    return jsonify({
        "message": "Evaluation completed",
        "accuracy": accuracy,
        "val_accuracy": val_accuracy
    }), 200



@flask_app.route("/classify_audio", methods=["POST"])
def classify_audio():
    data = request.get_json()
    file_path = data.get("file_path")
    if not file_path:
        return jsonify({"error": "Missing file_path"}), 400

    wav = convert_to_wav_if_needed(file_path)
    #patches = extractor.extract_features_from_file(wav)

    pred_result = classify_audio(wav, extractor, top_k=5)
    return jsonify(pred_result), 200


@flask_app.route("/processing", methods=["GET"])
def processing():
    return jsonify({"processing": processing_flag}), 200


@flask_app.route("/split_files", methods=["POST"])
def split_files():
    segment_length = request.get_json()["segment_length"]
    shorten.split_wav_files(SONGS_DIR, SNIPPETS_DIR, segment_length)
    return jsonify({"message": "Shortening completed"}), 200


@flask_app.route("/split_and_sort", methods=["POST"])
def split_and_sort():
    segment_length = request.get_json()["segment_length"]
    shorten.split_wav_files(SONGS_DIR, SNIPPETS_DIR, segment_length)
    sort.sort_and_delete_wav_files(SNIPPETS_DIR)
    return jsonify({"message": "Shortening and sorting completed"}), 200


@flask_app.route("/health", methods=["GET"])
def health():
    return jsonify(status="healthy", message="CNN service running"), 200


@flask_app.route("/evaluation_results")
def show_evaluation_results():
    results_dir = "/opt/application/evaluation_results"
    files = os.listdir(results_dir)

    # Filter out CSVs
    files = [f for f in files if not f.lower().endswith(".csv")]

    # Build HTML
    html = "<html><head><title>Evaluation Results</title></head><body>"
    html += f"<h2>Files in {results_dir}</h2><ul>"

    for f in sorted(files):
        path = os.path.join(results_dir, f)
        html += f'<li><a href="/evaluation_results/file/{f}">{f}</a></li>'

    html += "</ul></body></html>"
    return Response(html, mimetype="text/html")


@flask_app.route("/evaluation_results/file/<filename>")
def serve_result_file(filename):
    results_dir = "/opt/application/evaluation_results"
    path = os.path.join(results_dir, filename)
    if not os.path.exists(path):
        return "File not found", 404
    with open(path, "rb") as f:
        data = f.read()
    # Set MIME type based on extension
    ext = filename.lower().split(".")[-1]
    if ext == "png":
        mimetype = "image/png"
    else:
        mimetype = "text/html"
    return Response(data, mimetype=mimetype)


if __name__ == "__main__":
    #global cnn_model
    #cnn_model = load_model()
    flask_app.run(host="0.0.0.0", port=5002, debug=True)
