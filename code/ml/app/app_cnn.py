import os
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
from config.paths import (
    SNIPPETS_DIR,
    SONGS_DIR,
    CNN_MODEL_PATH,
    CNN_LABELS_PATH, EVALUATION_RESULTS_DIR
)
from features.dataset_creator_cnn import AudioDatasetCreatorCNN
from features.feature_extractor_cnn import AudioFeatureExtractorCNN
from flask import Flask, Response
from flask import request, jsonify
from training.model_cnn import (
    train_model,
    classify_audio
)
from training.model_evaluator import DanceModelEvaluator
from utilities import shorten, sort
from multiprocessing import Lock

flask_app = Flask(__name__)
cnn_model = None

csv_lock = Lock()

extractor = AudioFeatureExtractorCNN()
dataset_creator = AudioDatasetCreatorCNN(extractor)


def save_csv_threadsafe(dataset, rows):
    with csv_lock:
        dataset.save_csv(rows)


def convert_to_wav_if_needed_local(file_path):
    from utilities import file_converter
    if file_path.endswith(".wav"):
        return file_path
    if file_path.endswith(".webm"):
        return file_converter.convert_webm_to_wav(file_path, file_path.replace(".webm", ".wav"))
    if file_path.endswith(".caf"):
        return file_converter.convert_caf_to_wav(file_path, file_path.replace(".caf", ".wav"))
    return file_path


def run_task(file_paths_labels, output_dir):
    extractor = AudioFeatureExtractorCNN()
    rows = []

    for file_path, label in file_paths_labels:
        wav_path = convert_to_wav_if_needed_local(file_path)
        tensor = extractor.wav_to_spectrogram_tensor(wav_path)

        window_id = str(uuid.uuid4())
        save_path = output_dir / f"{window_id}.npz"
        np.savez(save_path, input=tensor, label=label)

        rows.append({
            "window_id": window_id,
            "filename": os.path.basename(wav_path),
            "label": label,
            "npy_path": str(save_path)
        })

    return rows


@flask_app.route("/process_all_audio", methods=["POST"])
def process_all_audio():
    data = request.get_json()
    deleteFiles = data.get("deleteFiles", False)
    worker_count = data.get("worker_count", 30)

    print(f"Starting processing all audio with {worker_count} workers")

    if deleteFiles:
        dataset_creator.clear_files()

    labels = os.listdir(SNIPPETS_DIR)
    processed_ids = dataset_creator.load_existing()

    tasks = []
    skipped = 0

    for label in labels:
        folder = os.path.join(SNIPPETS_DIR, label)
        wav_files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith((".wav", ".webm", ".caf"))
        ]

        for file_path in wav_files:
            if file_path in processed_ids:
                skipped += 1
                continue
            tasks.append((file_path, label))

    total = len(tasks)
    if total == 0:
        return jsonify({
            "message": "No new files to process",
            "skipped": skipped
        }), 200

    chunk_size = max(1, total // worker_count)
    chunks = [tasks[i:i + chunk_size] for i in range(0, total, chunk_size)]

    processed_count = 0
    errors = []

    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        futures = [
            executor.submit(run_task, chunk, dataset_creator.output_dir)
            for chunk in chunks
        ]

        for future in as_completed(futures):
            try:
                rows = future.result()
                dataset_creator.save_csv(rows)
                processed_count += len(rows)
                pct = processed_count / total
                print(f"Progress {processed_count}/{total} ({pct:.1%})")
            except Exception as e:
                errors.append(str(e))

    message = jsonify({
        "message": "Processing completed",
        "total": total,
        "skipped": skipped,
        "errors": len(errors)
    })

    print(message)

    if errors:
        print("Errors:")
        for err in errors:
            print(err)

    return message, 200



@flask_app.route("/train", methods=["POST"])
def train():
    data = request.get_json()
    disabled_labels = data.get("disabled_labels", [])
    test_size = data.get("test_size", 0.2)
    batch_size = data.get("batch_size", 512)
    epochs = data.get("epochs", 100)
    downsampling = data.get("downsampling", True)

    result = train_model(
        disabled_labels=disabled_labels,
        batch_size=batch_size,
        epochs=epochs,
        test_size=test_size,
        downsampling=downsampling
    )
    accuracy = result["accuracy"]
    val_accuracy = max(result["history"]["val_accuracy"])

    return jsonify({
        "message": "Training completed",
        "accuracy": accuracy,
        "val_accuracy": val_accuracy
    }), 200


@flask_app.route("/evaluate", methods=["GET"])
def evaluate():
    evaluator = DanceModelEvaluator(
        model_path=CNN_MODEL_PATH,
        labels_path=CNN_LABELS_PATH,
        output_dir=EVALUATION_RESULTS_DIR
    )

    evaluator.load_resources()

    results = evaluator.evaluate_all()

    return jsonify({
        "message": "Evaluation completed",
        "train_accuracy": results.get("train"),
        "val_accuracy": results.get("val"),
        "test_accuracy": results.get("test")
    }), 200


@flask_app.route("/classify_audio", methods=["POST"])
def classify():
    file_path = request.args.get('file_path')

    if not file_path:
        return jsonify({"error": "Missing file_path"}), 400

    wav = convert_to_wav_if_needed_local(file_path)
    # patches = extractor.extract_features_from_file(wav)

    pred_result = classify_audio(wav, extractor)
    return jsonify(pred_result), 200


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
    files = os.listdir(EVALUATION_RESULTS_DIR)

    # Filter out CSVs
    files = [f for f in files if not f.lower().endswith(".csv")]

    # Build HTML
    html = "<html><head><title>Evaluation Results</title></head><body>"
    html += f"<h2>Files in {EVALUATION_RESULTS_DIR}</h2><ul>"

    for f in sorted(files):
        path = os.path.join(EVALUATION_RESULTS_DIR, f)
        html += f'<li><a href="/evaluation_results/file/{f}">{f}</a></li>'

    html += "</ul></body></html>"
    return Response(html, mimetype="text/html")


@flask_app.route("/evaluation_results/file/<filename>")
def serve_result_file(filename):
    path = os.path.join(EVALUATION_RESULTS_DIR, filename)
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
    flask_app.run(host="0.0.0.0", port=5001, debug=True)
