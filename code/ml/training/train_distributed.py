import os
import tensorflow as tf
from training.model_cnn import train_model

strategy = tf.distribute.MultiWorkerMirroredStrategy()

batch_size = int(os.environ.get("BATCH_SIZE", 64))
epochs = int(os.environ.get("EPOCHS", 100))
disabled_labels = os.environ.get("DISABLED_LABELS", "").split(",") if os.environ.get("DISABLED_LABELS") else None
test_size = float(os.environ.get("TEST_SIZE", 0.1))
downsampling = os.environ.get("DOWNSAMPLING", "false").lower() == "true"

with strategy.scope():
    train_model(
        batch_size=batch_size,
        epochs=epochs,
        disabled_labels=disabled_labels,
        test_size=test_size,
        downsampling=downsampling
    )
