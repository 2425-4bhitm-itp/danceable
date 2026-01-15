import itertools
import json
import os
import time
import traceback
from datetime import datetime
from pathlib import Path

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf

from config.paths import HYPER_ENV_PATH, BASE_MODEL_DIR
from training.evaluate import evaluate_and_export
from training.model_cnn import train_model

POD_NAME = os.environ["POD_NAME"]
REPLICAS = int(os.environ["REPLICAS"])

RUN_ID_FILE = Path(HYPER_ENV_PATH) / "RUN_ID"
STATE_FILE = Path(HYPER_ENV_PATH) / "STATE"
READY_FILE = Path(HYPER_ENV_PATH) / "READY_WORKERS"
RESET_LOCK_FILE = Path(HYPER_ENV_PATH) / "RESET_LOCK"
EVAL_LOCK_FILE = Path(HYPER_ENV_PATH) / "HYPER_LOCK"

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


def acquire_eval_lock():
    try:
        fd = os.open(EVAL_LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, POD_NAME.encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False


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


def make_hashable(x):
    if isinstance(x, list):
        return tuple(make_hashable(i) for i in x)
    if isinstance(x, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in x.items()))
    return x


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
        print(f"is chief: {is_chief()}")

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

            if is_chief():
                HYPER_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

            total_runs = len(train_runs) * len(model_runs)
            current_index = 0

            for train_vals in train_runs:
                train_cfg = dict(zip(train_keys, train_vals))
                print("train run: " + str(train_vals))

                for model_vals in model_runs:
                    model_cfg = dict(zip(model_keys, model_vals))
                    hashable_train = tuple(make_hashable(v) for v in train_vals)
                    hashable_model = tuple(make_hashable(v) for v in model_vals)
                    config_hash = hash(hashable_train + hashable_model) & 0xffff

                    run_tag = f"{current_run}_{config_hash:x}"

                    current_index += 1
                    print("model run: " + str(model_vals))
                    print(str(current_index) + "/" + str(total_runs))

                    checkpoint_directory = BASE_MODEL_DIR / f"hyper/{run_tag}_weights.h5"
                    start_time = time.time()
                    with strategy.scope():
                        train_model(
                            batch_size=train_cfg.get("batch_size", 128),
                            epochs=train_cfg.get("epochs", 100),
                            model_config=model_cfg,
                            verbose=0,
                            checkpoint_dir=checkpoint_directory
                        )

                    elapsed_time = time.time() - start_time

                    if acquire_eval_lock():
                        print(f"{POD_NAME} acquired evaluation lock")
                        try:
                            loss, accuracy, labels, input_shape = evaluate_and_export(model_cfg, checkpoint_directory)
                        finally:
                            os.remove(EVAL_LOCK_FILE)

                        results = ({
                            "timestamp": datetime.utcnow().isoformat(),
                            "train_config": train_cfg,
                            "model_config": model_cfg,
                            "elapsed_seconds": elapsed_time,
                            "loss": loss,
                            "accuracy": accuracy,
                            "labels": labels,
                            "input_shape": input_shape
                        })
                        print("appending results: " + str(results))

                        summary_file = HYPER_RESULTS_DIR / f"results_{run_tag}.json"
                        json.dump(results, open(summary_file, "w"), indent=2)

            if is_chief():
                result_files = sorted(HYPER_RESULTS_DIR.glob(f"results_*.json"))
                merged = []
                for fpath in result_files:
                    try:
                        merged.append(json.load(open(fpath)))
                    except:
                        continue
                summary_path = HYPER_RESULTS_DIR / f"summary.json"
                json.dump(merged, open(summary_path, "w"), indent=2)
                for fpath in result_files:
                    try:
                        fpath.unlink()
                    except:
                        pass

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
