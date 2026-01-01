import itertools
import json
import os
import time
import traceback
from datetime import datetime
from pathlib import Path

import tensorflow as tf

from config.paths import HYPER_ENV_PATH
from training.model_cnn import train_model

POD_NAME = os.environ["POD_NAME"]
REPLICAS = int(os.environ["REPLICAS"])

RUN_ID_FILE = Path(HYPER_ENV_PATH) / "RUN_ID"
STATE_FILE = Path(HYPER_ENV_PATH) / "STATE"
READY_FILE = Path(HYPER_ENV_PATH) / "READY_WORKERS"
RESET_LOCK_FILE = Path(HYPER_ENV_PATH) / "RESET_LOCK"

HYPER_RESULTS_DIR = Path("/app/song-storage/hyper_runs")

last_seen_run = -1

print(f"{POD_NAME} started")


def is_chief():
    tf_config = json.loads(os.environ.get("TF_CONFIG", "{}"))
    task = tf_config.get("task", {})
    return task.get("type") == "worker" and task.get("index") == 0


def acquire_reset_lock():
    os.makedirs(HYPER_ENV_PATH, exist_ok=True)
    try:
        fd = os.open(RESET_LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, POD_NAME.encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False


def wait_for_reset_completion():
    while RESET_LOCK_FILE.exists():
        time.sleep(0.5)


def initialize_hyper_files():
    if acquire_reset_lock():
        with open(RUN_ID_FILE, "w") as f:
            f.write("-1")
        with open(STATE_FILE, "w") as f:
            f.write("idle")
        print(f"{POD_NAME} performed hyper reset")
        os.remove(RESET_LOCK_FILE)
    else:
        wait_for_reset_completion()


def register_ready():
    os.makedirs(HYPER_ENV_PATH, exist_ok=True)
    while True:
        try:
            workers = set()
            if READY_FILE.exists():
                with open(READY_FILE, "r") as f:
                    workers = {line.strip() for line in f if line.strip()}

            if POD_NAME not in workers:
                workers.add(POD_NAME)
                with open(READY_FILE, "w") as f:
                    for w in sorted(workers):
                        f.write(w + "\n")
            return
        except Exception:
            time.sleep(1)


def run_hyperparameter_search():
    global last_seen_run

    while True:
        if not RUN_ID_FILE.exists():
            time.sleep(1)
            continue

        current_run = int(RUN_ID_FILE.read_text().strip())
        if current_run <= last_seen_run:
            time.sleep(1)
            continue

        last_seen_run = current_run
        print(f"{POD_NAME} starting hyper run {current_run}")

        try:
            search_space_file = Path(HYPER_ENV_PATH) / "SEARCH_SPACE"
            search_space = json.load(open(search_space_file))

            train_space = search_space.get("train", {})
            model_space = search_space.get("model", {})

            train_keys = list(train_space.keys())
            model_keys = list(model_space.keys())

            train_runs = list(itertools.product(*train_space.values())) or [()]
            model_runs = list(itertools.product(*model_space.values())) or [()]

            strategy = tf.distribute.MultiWorkerMirroredStrategy()

            run_results = []

            if is_chief():
                HYPER_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

            for train_vals in train_runs:
                train_cfg = dict(zip(train_keys, train_vals))

                for model_vals in model_runs:
                    model_cfg = dict(zip(model_keys, model_vals))
                    run_tag = f"{current_run}_{hash(tuple(train_vals) + tuple(model_vals)) & 0xffff:x}"
                    print(f"{POD_NAME} running config {run_tag}")

                    start_time = time.time()
                    history = {}
                    with strategy.scope():
                        # add callback to capture metrics per epoch
                        class CaptureHistory(tf.keras.callbacks.Callback):
                            def on_epoch_end(self, epoch, logs=None):
                                logs = logs or {}
                                for k, v in logs.items():
                                    history.setdefault(k, []).append(float(v))

                        metrics = train_model(
                            batch_size=train_cfg.get("batch_size", 128),
                            epochs=train_cfg.get("epochs", 100),
                            test_size=train_cfg.get("test_size", 0.2),
                            downsampling=train_cfg.get("downsampling", True),
                            disabled_labels=train_cfg.get("disabled_labels"),
                            model_config=model_cfg,
                        )

                    elapsed_time = time.time() - start_time

                    if is_chief():
                        run_results.append({
                            "run_tag": run_tag,
                            "timestamp": datetime.utcnow().isoformat(),
                            "train_config": train_cfg,
                            "model_config": model_cfg,
                            "metrics": history,
                            "elapsed_seconds": elapsed_time
                        })

            if is_chief():
                summary_file = HYPER_RESULTS_DIR / f"summary_{current_run}.json"
                json.dump(run_results, open(summary_file, "w"), indent=2)
                with open(STATE_FILE, "w") as f:
                    f.write("idle")

            print(f"{POD_NAME} finished hyper run {current_run}")

        except Exception:
            print(f"Error during hyper run {current_run}:\n{traceback.format_exc()}")
            time.sleep(1)


initialize_hyper_files()
register_ready()
print(f"{POD_NAME} registered as ready")
run_hyperparameter_search()
