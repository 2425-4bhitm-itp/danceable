import os
import tensorflow as tf
from training.model_cnn import train_model

strategy = tf.distribute.MultiWorkerMirroredStrategy()

batch_size = int(os.environ.get("BATCH_SIZE", 64))
epochs = int(os.environ.get("EPOCHS", 100))

with strategy.scope():
    train_model(batch_size=batch_size, epochs=epochs)
