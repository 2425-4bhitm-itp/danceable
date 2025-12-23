import os
import time
import tensorflow as tf
from training.model_cnn import train_model
from config.paths import TRAIN_ENV_PATH

POD_NAME = os.environ["POD_NAME"]
REPLICAS = int(os.environ["REPLICAS"])

training_id_file = os.path.join(TRAIN_ENV_PATH, "TRAINING_ID")
state_file = os.path.join(TRAIN_ENV_PATH, "TRAINING_STATE")
ready_file = os.path.join(TRAIN_ENV_PATH, "READY_WORKERS")

last_seen_id = -1

print(f"{POD_NAME} started")

def read_env_file(name, default=None):
    try:
        return open(os.path.join(TRAIN_ENV_PATH, name)).read().strip()
    except Exception:
        return default


def register_ready():
    os.makedirs(TRAIN_ENV_PATH, exist_ok=True)

    while True:
        try:
            if os.path.exists(ready_file):
                with open(ready_file, "r") as f:
                    workers = {line.strip() for line in f if line.strip()}
            else:
                workers = set()

            if POD_NAME not in workers:
                workers.add(POD_NAME)
                with open(ready_file, "w") as f:
                    for w in sorted(workers):
                        f.write(w + "\n")

            return
        except Exception:
            time.sleep(1)


register_ready()
print(f"{POD_NAME} registered as ready")


while True:
    if not os.path.isfile(training_id_file):
        time.sleep(1)
        continue

    current_id = int(open(training_id_file).read().strip())

    if current_id <= last_seen_id:
        time.sleep(1)
        continue

    last_seen_id = current_id
    print(f"{POD_NAME} starting training run {current_id}")

    batch_size = int(read_env_file("BATCH_SIZE", "64"))
    epochs = int(read_env_file("EPOCHS", "100"))
    disabled_labels = read_env_file("DISABLED_LABELS", "")
    disabled_labels = disabled_labels.split(",") if disabled_labels else None
    test_size = float(read_env_file("TEST_SIZE", "0.1"))
    downsampling = read_env_file("DOWNSAMPLING", "false").lower() == "true"

    strategy = tf.distribute.MultiWorkerMirroredStrategy()

    with strategy.scope():
        train_model(
            batch_size=batch_size,
            epochs=epochs,
            disabled_labels=disabled_labels,
            test_size=test_size,
            downsampling=downsampling
        )

    print(f"{POD_NAME} finished training run {current_id}")

    if POD_NAME == "ml-train-0":
        with open(state_file, "w") as f:
            f.write("idle")
