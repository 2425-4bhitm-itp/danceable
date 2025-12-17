import os
import time
import tensorflow as tf
from training.model_cnn import train_model
from config.paths import TRAIN_ENV_PATH

REPLICAS = int(os.environ.get("REPLICAS", 4))
POD_NAME = os.environ.get("POD_NAME")

start_file = os.path.join(TRAIN_ENV_PATH, "START_TRAINING")
while not os.path.exists(start_file) or open(start_file).read().strip().lower() != "true":
    time.sleep(1)

def read_env_file(name, default=None):
    try:
        return open(os.path.join(TRAIN_ENV_PATH, name)).read().strip()
    except Exception:
        return default

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
