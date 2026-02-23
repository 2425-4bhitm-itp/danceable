import concurrent.futures
import json
import os
import time
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from config.paths import (
    SNIPPETS_DIR,
    SONGS_DIR,
    CNN_MODEL_PATH,
    CNN_LABELS_PATH,
    EVALUATION_RESULTS_DIR,
    TRAIN_ENV_PATH,
    HYPER_ENV_PATH,
    CNN_DATASET_PATH,
    CNN_WEIGHTS_PATH
)
from features.dataset_creator_cnn import AudioDatasetCreatorCNN
from features.feature_extractor_cnn import AudioFeatureExtractorCNN
from flask import Flask, request, jsonify, Response
from training.model_cnn import (
    classify_audio
)
from training.model_evaluator import DanceModelEvaluator
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

    window_id = str(uuid.uuid4())
    save_path = dataset_creator.output_dir / f"{window_id}.npz"

    np.savez(save_path, input=tensor, label=label)

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

    data = request.get_json()
    worker_count = data.get("worker_count", 1)
    delete_files = data.get("delete_files", False)

    print(f"Worker count set to: {worker_count}")
    print(f"Available CPU cores: {os.cpu_count()}")

    if delete_files:
        dataset_creator.clear_files()
        print("Cleared existing processed files")

    labels = os.listdir(SNIPPETS_DIR)
    print(f"Starting audio processing for {len(labels)} labels")

    processed_files = dataset_creator.load_existing()

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
            raise

    processed_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
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

    batch_size = str(data.get("batch_size", 512))
    epochs = str(data.get("epochs", 100))
    disabled_labels = data.get("disabled_labels", [])
    test_size = float(data.get("test_size", 0.2))
    downsampling = bool(data.get("downsampling", False))
    model_config = data.get("model_config", {})

    os.makedirs(TRAIN_ENV_PATH, exist_ok=True)

    state_file = os.path.join(TRAIN_ENV_PATH, "TRAINING_STATE")
    id_file = os.path.join(TRAIN_ENV_PATH, "TRAINING_ID")

    if os.path.exists(state_file):
        if open(state_file).read().strip() != "idle":
            return jsonify({"error": "Training already running"}), 409

    with open(state_file, "w") as f:
        f.write("preparing")

    dataset_creator.prepare_dataset_once(
        disabled_labels=disabled_labels,
        downsampling=downsampling,
        test_size=test_size,
        val_from_test=0.5
    )

    meta_path = CNN_DATASET_PATH / "meta.json"
    with open(meta_path, "r") as f:
        meta = json.load(f)

    sample_path = meta["filtered_csv"]
    df = pd.read_csv(sample_path)
    sample = np.load(df.iloc[0]["npy_path"])["input"].astype(np.float32)
    while sample.ndim > 3:
        sample = sample.squeeze(0)
    if sample.ndim == 2:
        sample = sample[..., np.newaxis]

    meta["model_config"] = {
        "input_shape": list(sample.shape),
        "num_classes": len(meta["labels"]),
        **model_config,
    }

    with open(meta_path, "w") as f:
        json.dump(meta, f)

    with open(os.path.join(TRAIN_ENV_PATH, "MODEL_CONFIG"), "w") as f:
        json.dump(model_config, f)  # writes {} if not provided

    with open(os.path.join(TRAIN_ENV_PATH, "BATCH_SIZE"), "w") as f:
        f.write(batch_size)
    with open(os.path.join(TRAIN_ENV_PATH, "EPOCHS"), "w") as f:
        f.write(epochs)

    current = int(open(id_file).read().strip()) if os.path.exists(id_file) else 0
    with open(id_file, "w") as f:
        f.write(str(current + 1))

    with open(state_file, "w") as f:
        f.write("running")

    return jsonify({"message": "Training started"}), 200


@flask_app.route("/evaluate", methods=["GET"])
def evaluate():
    evaluator = DanceModelEvaluator(
        model_path=CNN_WEIGHTS_PATH,
        output_dir=EVALUATION_RESULTS_DIR,
        meta_path=CNN_DATASET_PATH / "meta.json",
    )

    evaluator.load_resources()
    results = evaluator.evaluate_all()

    print(results)

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

    wav = convert_to_wav_if_needed(file_path)

    pred_result = classify_audio(wav, extractor)
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
    ext = filename.lower().split(".")[-1]
    if ext == "png":
        mimetype = "image/png"
    else:
        mimetype = "text/html"
    return Response(data, mimetype=mimetype)


@flask_app.route("/hyperparameter-test", methods=["POST"])
def hyperparameter_test():
    data = request.get_json()
    search_space = data.get("search_space")
    if not search_space:
        return jsonify({"error": "search_space required"}), 400

    replicas = int(data.get("replicas"))

    run_id = int(time.time())
    run_dir = Path(HYPER_ENV_PATH) / f"run_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    json.dump(search_space, open(run_dir / "search_space.json", "w"), indent=2)

    dataset_creator.prepare_dataset_once(
        disabled_labels=search_space.get("train", {}).get("disabled_labels", []),
        downsampling=search_space.get("train", {}).get("downsampling", [False])[0],
        test_size=search_space.get("train", {}).get("test_size", [0.2])[0],
        val_from_test=0.5,
    )

    runs = expand_search_space(search_space)
    shards = split_runs(runs, replicas)

    for i, shard in enumerate(shards):
        json.dump(
            shard,
            open(run_dir / f"runs_{i}.json", "w"),
            indent=2,
        )

    return jsonify({
        "run_id": run_id,
        "total_runs": len(runs),
        "replicas": replicas,
    }), 200


def init_train_env():
    defaults = {
        "BATCH_SIZE": "512",
        "EPOCHS": "100",
        "DISABLED_LABELS": "",
        "TEST_SIZE": "0.1",
        "DOWNSAMPLING": "false",
        "TRAINING_ID": "-1",
        "TRAINING_STATE": "idle"
    }

    os.makedirs(TRAIN_ENV_PATH, exist_ok=True)

    for k, v in defaults.items():
        path = os.path.join(TRAIN_ENV_PATH, k)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(v)


def split_runs(runs: list[dict], replicas: int) -> list[list[dict]]:
    shards = [[] for _ in range(replicas)]
    for i, run in enumerate(runs):
        shards[i % replicas].append(run)
    return shards


def expand_search_space(search_space: dict) -> list[dict]:
    import itertools

    train_space = search_space.get("train", {})
    model_space = search_space.get("model", {})

    train_keys = list(train_space.keys())
    model_keys = list(model_space.keys())

    train_runs = list(itertools.product(*train_space.values())) or [()]
    model_runs = list(itertools.product(*model_space.values())) or [()]

    runs = []
    for t_vals in train_runs:
        for m_vals in model_runs:
            runs.append({
                "train": dict(zip(train_keys, t_vals)),
                "model": dict(zip(model_keys, m_vals)),
            })

    return runs


if __name__ == "__main__":
    init_train_env()
    flask_app.run(host="0.0.0.0", port=5001, debug=True)
