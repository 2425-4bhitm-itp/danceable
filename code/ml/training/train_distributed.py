import os
import time

import tensorflow as tf

from config.paths import TRAIN_ENV_PATH
from training.evaluate import evaluate_and_export
from training.model_cnn import train_model

POD_NAME = os.environ.get("POD_NAME", "unknown-pod")

training_id_file = os.path.join(TRAIN_ENV_PATH, "TRAINING_ID")
state_file = os.path.join(TRAIN_ENV_PATH, "TRAINING_STATE")
ready_file = os.path.join(TRAIN_ENV_PATH, "READY_WORKERS")

reset_lock_file = os.path.join(TRAIN_ENV_PATH, "RESET_LOCK")
eval_lock_file = os.path.join(TRAIN_ENV_PATH, "EVAL_LOCK")

last_seen_id = -1

print(f"{POD_NAME} started")


def read_env_file(name, default=None):
    try:
        with open(os.path.join(TRAIN_ENV_PATH, name)) as f:
            return f.read().strip()
    except Exception:
        return default


# -----------------------
# Reset handling (PVC-safe)
# -----------------------

def acquire_reset_lock():
    os.makedirs(TRAIN_ENV_PATH, exist_ok=True)
    try:
        fd = os.open(reset_lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, POD_NAME.encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False


def wait_for_reset_completion():
    while os.path.exists(reset_lock_file):
        time.sleep(0.5)


def initialize_training_files():
    if acquire_reset_lock():
        with open(training_id_file, "w") as f:
            f.write("-1")
        with open(state_file, "w") as f:
            f.write("idle")
        if os.path.exists(ready_file):
            os.remove(ready_file)
        print(f"{POD_NAME} performed training reset")
        os.remove(reset_lock_file)
    else:
        wait_for_reset_completion()


# -----------------------
# Worker registration
# -----------------------

def register_ready():
    os.makedirs(TRAIN_ENV_PATH, exist_ok=True)
    while True:
        try:
            workers = set()
            if os.path.exists(ready_file):
                with open(ready_file) as f:
                    workers = {l.strip() for l in f if l.strip()}

            if POD_NAME not in workers:
                workers.add(POD_NAME)
                with open(ready_file, "w") as f:
                    for w in sorted(workers):
                        f.write(w + "\n")
            return
        except Exception:
            time.sleep(1)


# -----------------------
# Evaluation lock
# -----------------------

def acquire_eval_lock():
    try:
        fd = os.open(eval_lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, POD_NAME.encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False


# -----------------------
# Startup sequence
# -----------------------

initialize_training_files()
register_ready()

print(f"{POD_NAME} registered as ready")

# -----------------------
# Main loop
# -----------------------

while True:
    if not os.path.exists(training_id_file):
        time.sleep(1)
        continue

    try:
        current_id = int(open(training_id_file).read().strip())
    except Exception:
        time.sleep(1)
        continue

    if current_id <= last_seen_id:
        time.sleep(1)
        continue

    last_seen_id = current_id
    print(f"{POD_NAME} starting training run {current_id}")

    batch_size = int(read_env_file("BATCH_SIZE", "128"))
    epochs = int(read_env_file("EPOCHS", "100"))

    strategy = tf.distribute.MultiWorkerMirroredStrategy()

    with strategy.scope():
        train_model(
            batch_size=batch_size,
            epochs=epochs,
            verbose=1
        )

    print(f"{POD_NAME} finished training run {current_id}")

    if acquire_eval_lock():
        print(f"{POD_NAME} acquired evaluation lock")
        try:
            evaluate_and_export()
            with open(state_file, "w") as f:
                f.write("idle")
        finally:
            os.remove(eval_lock_file)
