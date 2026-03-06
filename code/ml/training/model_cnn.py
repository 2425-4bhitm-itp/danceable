import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from sympy import true
from tensorflow.keras.layers import (
    Conv2D,
    MaxPooling2D,
    Flatten,
    Dense,
    Dropout,
    BatchNormalization,
)
from tensorflow.keras.models import Sequential
from tensorflow.python.data.ops.options import AutoShardPolicy

from config.paths import (
    CNN_DATASET_PATH,
    CNN_WEIGHTS_PATH,
    SCALER_PATH, CNN_MODEL_PATH, CNN_LABELS_PATH,
)

# ---------------------------------------------------------------------
# CPU / threading configuration
# ---------------------------------------------------------------------

os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())
os.environ["MKL_NUM_THREADS"] = str(os.cpu_count())

tf.config.threading.set_intra_op_parallelism_threads(os.cpu_count())
tf.config.threading.set_inter_op_parallelism_threads(os.cpu_count())

_scaler = None
_labels = None
_model = None
# ---------------------------------------------------------------------
# Model definition
# ---------------------------------------------------------------------

def build_cnn(
        input_shape: tuple,
        num_classes: int,
        filters=(64, 128, 256),
        kernel_size=(7, 7),
        dense_units=512,
        dropout_rate=0.3,
        learning_rate=0.0001,
) -> tf.keras.Model:
    model = Sequential()

    for i, f in enumerate(filters):
        if i == 0:
            model.add(
                Conv2D(
                    f,
                    kernel_size,
                    activation="relu",
                    padding="same",
                    input_shape=input_shape,
                )
            )
        else:
            model.add(
                Conv2D(
                    f,
                    kernel_size,
                    activation="relu",
                    padding="same",
                )
            )

        model.add(BatchNormalization())
        model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(dense_units, activation="relu"))
    model.add(Dropout(dropout_rate))
    model.add(Dense(num_classes, activation="softmax"))

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

    model.compile(
        optimizer=optimizer,
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model


# ---------------------------------------------------------------------
# Dataset loading utilities
# ---------------------------------------------------------------------

def load_dataset_csv(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    df = pd.read_csv(csv_path)

    required = {"window_id", "filename", "label", "npy_path"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")

    return df


def load_npy(path, input_shape):
    arr = np.load(path.decode())["input"].astype(np.float32)

    while arr.ndim > 3:
        arr = np.squeeze(arr, axis=0)

    if arr.ndim == 2:
        arr = arr[..., np.newaxis]

    return arr.reshape(input_shape)

def augment(x, y):
    # Frequency masking — blank out random frequency bands
    freq_mask_size = tf.random.uniform([], 0, 20, dtype=tf.int32)
    f0 = tf.random.uniform([], 0, tf.shape(x)[0] - freq_mask_size, dtype=tf.int32)
    mask = tf.concat([
        tf.ones([f0, tf.shape(x)[1], tf.shape(x)[2]]),
        tf.zeros([freq_mask_size, tf.shape(x)[1], tf.shape(x)[2]]),
        tf.ones([tf.shape(x)[0] - f0 - freq_mask_size, tf.shape(x)[1], tf.shape(x)[2]]),
    ], axis=0)
    x = x * mask

    # Time masking — blank out random time steps
    time_mask_size = tf.random.uniform([], 0, 20, dtype=tf.int32)
    t0 = tf.random.uniform([], 0, tf.shape(x)[1] - time_mask_size, dtype=tf.int32)
    mask_t = tf.concat([
        tf.ones([tf.shape(x)[0], t0, tf.shape(x)[2]]),
        tf.zeros([tf.shape(x)[0], time_mask_size, tf.shape(x)[2]]),
        tf.ones([tf.shape(x)[0], tf.shape(x)[1] - t0 - time_mask_size, tf.shape(x)[2]]),
    ], axis=1)
    x = x * mask_t

    # Additive Gaussian noise
    x = x + tf.random.normal(tf.shape(x), stddev=0.05)

    return x, y

def make_tf_dataset(
        paths,
        labels,
        input_shape,
        num_classes,
        batch_size,
        shuffle,
):
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))

    if shuffle:
        ds = ds.shuffle(buffer_size=len(paths), seed=42)

    def map_fn(path, label):
        x = tf.numpy_function(
            load_npy,
            [path, input_shape],
            tf.float32,
        )
        x.set_shape(input_shape)

        y = tf.one_hot(
            tf.cast(label, tf.int32),
            depth=num_classes,
        )
        y = tf.cast(y, tf.float32)

        return x, y

    ds = ds.map(map_fn, num_parallel_calls=tf.data.AUTOTUNE)

    if shuffle:
        ds = ds.map(augment, num_parallel_calls=tf.data.AUTOTUNE)

    ds = ds.batch(batch_size, drop_remainder=True)

    options = tf.data.Options()
    options.experimental_distribute.auto_shard_policy = AutoShardPolicy.DATA
    ds = ds.with_options(options)

    ds = ds.prefetch(tf.data.AUTOTUNE)

    return ds


# ---------------------------------------------------------------------
# Prepared dataset loader
# ---------------------------------------------------------------------

def load_prepared_dataset():
    meta_path = Path(CNN_DATASET_PATH) / "meta.json"

    with open(meta_path) as f:
        meta = json.load(f)

    filtered_csv = meta["filtered_csv"]
    df = pd.read_csv(filtered_csv)

    label_to_idx = meta["label_to_idx"]

    train_idx = meta["train_idx"]
    val_idx = meta["val_idx"]

    train_paths = df.iloc[train_idx]["npy_path"].astype(str).tolist()
    val_paths = df.iloc[val_idx]["npy_path"].astype(str).tolist()

    train_labels = [
        label_to_idx[df.iloc[i]["label"]]
        for i in train_idx
    ]

    val_labels = [
        label_to_idx[df.iloc[i]["label"]]
        for i in val_idx
    ]

    scaler = joblib.load(SCALER_PATH)

    return (
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        meta,
        scaler,
    )


# ---------------------------------------------------------------------
# Training entry point
# ---------------------------------------------------------------------

def train_model(
        batch_size: int = 128,
        epochs: int = 100,
        model_config: dict | None = None,
        verbose: int = 1,
        checkpoint_dir: Path = CNN_WEIGHTS_PATH
):
    (
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        meta,
        scaler,
    ) = load_prepared_dataset()

    num_classes = len(meta["labels"])

    sample = np.load(train_paths[0])["input"].astype(np.float32)
    while sample.ndim > 3:
        sample = sample.squeeze(0)
    if sample.ndim == 2:
        sample = sample[..., np.newaxis]

    input_shape = sample.shape

    train_ds = make_tf_dataset(
        train_paths, train_labels, input_shape, num_classes, batch_size, shuffle=True,
    )
    val_ds = make_tf_dataset(
        val_paths, val_labels, input_shape, num_classes, batch_size, shuffle=False,
    )

    effective_config = model_config or {}

    model = build_cnn(
        input_shape=input_shape,
        num_classes=num_classes,
        **effective_config,
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=12,
            restore_best_weights=True,
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(checkpoint_dir),
            monitor="val_loss",
            save_best_only=True,
            save_weights_only=True,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=5,
            min_lr=1e-6,
        ),
    ]

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks,
        verbose=verbose,
    )

    return model

# ----------------------- Inference -----------------------

def set_model_None():
    global _model, _scaler, _labels
    _model = None
    _scaler = None
    _labels = None

def classify_audio(file_path: str, extractor) -> dict:
    global _model, _scaler, _labels

    if _model is None:
        _model = tf.keras.models.load_model(CNN_MODEL_PATH)
        print("loaded model")
    if _scaler is None:
        _scaler = joblib.load(SCALER_PATH)
    if _labels is None:
        with open(CNN_LABELS_PATH) as f:
            _labels = json.load(f)

    assert len(_labels) == _model.output_shape[-1], (
        f"Label count {len(_labels)} != model outputs {_model.output_shape[-1]}. "
        "CNN_LABELS_PATH is out of sync — retrain or fix the label file."
    )

    patches = extractor.extract_features_from_file(file_path, true)
    if not patches:
        raise ValueError("No patches extracted")

    batch = np.asarray(patches, dtype=np.float32)

    if batch.ndim == 5 and batch.shape[1] == 1:
        batch = batch[:, 0]

    mean = _scaler["mean"]
    std = _scaler["std"]

    batch = (batch - mean) / (std + 1e-8)

    temperature = 1.5  # tune between 1.2–2.5; higher = flatter/less confident
    probs = _model.predict(batch, verbose=0)
    log_probs = np.log(probs + 1e-8) / temperature
    probs = np.exp(log_probs - log_probs.max(axis=-1, keepdims=True))  # numerically stable
    probs = probs / probs.sum(axis=-1, keepdims=True)
    avg = probs.mean(axis=0)

    pairs = sorted(
        zip(_labels, avg.tolist()),
        key=lambda x: x[1],
        reverse=True
    )

    print("model output shape" + str(_model.output_shape))
    print("length of labels variable" + str(len(_labels)))
    print("labels: " + str(_labels))
    print("pairs: "+ str(pairs))

    return {
        "predictions": [
            {"danceName": label, "confidence": float(f"{conf:.6f}")}
            for label, conf in pairs
        ]
    }


def load_model():
    global _model, _scaler
    _model = tf.keras.models.load_model(CNN_MODEL_PATH)
    _scaler = joblib.load(SCALER_PATH)
