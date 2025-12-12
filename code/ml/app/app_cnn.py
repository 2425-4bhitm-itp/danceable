import os
import uuid

import numpy as np
from config.paths import (
    SNIPPETS_DIR,
    SONGS_DIR,
    CNN_MODEL_PATH,
    CNN_LABELS_PATH, EVALUATION_RESULTS_DIR
)
from features.dataset_creator_cnn import AudioDatasetCreatorCNN
from features.feature_extractor_cnn import AudioFeatureExtractorCNN
from flask import Flask, request, jsonify, Response
from kubernetes import client, config
from training.model_cnn import (
    train_model,
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
    data = request.get_json()
    deleteFiles = data.get("deleteFiles", False)

    if deleteFiles:
        dataset_creator.clear_files()

    labels = os.listdir(SNIPPETS_DIR)
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
        return jsonify({"message": "No new files to process", "skipped": skipped}), 200

    task_file = Path("/app/tasks.json")
    with open(task_file, "w") as f:
        json.dump(tasks, f)

    config.load_incluster_config()
    batch = client.BatchV1Api()

    job_id = str(uuid.uuid4())[:8]
    job_name = f"ml-audio-processing-{job_id}"
    parallelism = 10

    container = client.V1Container(
        name="worker",
        image="ghcr.io/2425-4bhitm-itp/ml:latest",
        command=["python", "-u", "app.worker.py"],
        env=[
            client.V1EnvVar(name="JOB_PARALLELISM", value=str(parallelism)),
            client.V1EnvVar(
                name="JOB_COMPLETION_INDEX",
                value_from=client.V1EnvVarSource(
                    field_ref=client.V1ObjectFieldSelector(
                        field_path="metadata.annotations['batch.kubernetes.io/job-completion-index']"
                    )
                )
            )
        ],
        volume_mounts=[
            client.V1VolumeMount(
                name="song-volume",
                mount_path="/app/song-storage"
            )
        ]
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "ml-worker"}),
        spec=client.V1PodSpec(
            restart_policy="Never",
            containers=[container],
            volumes=[
                client.V1Volume(
                    name="song-volume",
                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                        claim_name="song-volume-claim"
                    )
                )
            ]
        )
    )

    job_spec = client.V1JobSpec(
        parallelism=parallelism,
        completions=parallelism,
        completion_mode="Indexed",
        template=template
    )

    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name),
        spec=job_spec
    )

    batch.create_namespaced_job(namespace="default", body=job)

    return jsonify({
        "message": "Batch processing job started",
        "total_tasks": total,
        "skipped": skipped,
        "job_name": job_name
    }), 200


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

    wav = convert_to_wav_if_needed(file_path)
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
    # global cnn_model
    # cnn_model = load_model()
    flask_app.run(host="0.0.0.0", port=5001, debug=True)
