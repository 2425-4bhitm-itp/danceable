import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import GroupShuffleSplit, StratifiedShuffleSplit
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.models import Sequential

from config.paths import CNN_MODEL_PATH, SCALER_PATH, CNN_LABELS_PATH, CNN_OUTPUT_CSV, CNN_DATASET_PATH, \
    CNN_WEIGHTS_PATH

# ----------------------- Threading / CPU Optimization -----------------------
tf.config.threading.set_intra_op_parallelism_threads(os.cpu_count())
tf.config.threading.set_inter_op_parallelism_threads(os.cpu_count())
os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())
os.environ["MKL_NUM_THREADS"] = str(os.cpu_count())

_model = None
_scaler = None
_labels = None


# ----------------------- Dataset Utilities -----------------------

def prepare_dataset(csv_path: Path, disabled_labels=None, downsampling=True, test_size=0.2, val_from_test=0.5):
    global _labels
    df = pd.read_csv(csv_path)
    if disabled_labels:
        df = df[~df["label"].isin(disabled_labels)]
        if df.empty:
            raise ValueError("All labels removed by disabled_labels")

    splits_file = Path(CNN_DATASET_PATH) / "splits.json"
    Path(CNN_DATASET_PATH).mkdir(parents=True, exist_ok=True)

    if is_chief():
        if downsampling:
            counts = df["label"].value_counts()
            min_count = counts.min()
            df = pd.concat([df[df["label"] == lbl].sample(min_count, random_state=42)
                            for lbl in counts.index]).sample(frac=1.0, random_state=42).reset_index(drop=True)

        _labels = sorted(df["label"].unique())
        label_to_idx = {l: i for i, l in enumerate(_labels)}

        df["song_id"] = df["filename"].apply(lambda x: str(x).split("_part")[0])
        X_idx = np.arange(len(df))
        y = df["label"].values
        groups = df["song_id"].values

        gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
        train_idx, temp_idx = next(gss.split(X_idx, y, groups=groups))

        temp_y = y[temp_idx]
        sss = StratifiedShuffleSplit(n_splits=1, test_size=val_from_test, random_state=42)
        val_rel_idx, test_rel_idx = next(sss.split(temp_idx.reshape(-1, 1), temp_y))

        val_idx = temp_idx[val_rel_idx]
        test_idx = temp_idx[test_rel_idx]

        json.dump({
            "train_idx": train_idx.tolist(),
            "val_idx": val_idx.tolist(),
            "test_idx": test_idx.tolist(),
            "labels": _labels
        }, open(splits_file, "w"))

    while not splits_file.exists():
        tf.print("Waiting for chief to prepare dataset...")
        tf.sleep(1)

    meta = json.load(open(splits_file))
    train_idx = np.array(meta["train_idx"])
    val_idx = np.array(meta["val_idx"])
    test_idx = np.array(meta["test_idx"])
    _labels = meta["labels"]
    label_to_idx = {l: i for i, l in enumerate(_labels)}

    scaler_file = SCALER_PATH
    if is_chief():
        sample_paths = df.iloc[train_idx]["npy_path"].tolist()
        s_sum, s_sq_sum, count = 0.0, 0.0, 0
        for p in sample_paths[:5000]:
            arr = np.load(p)["input"].astype(np.float32).ravel()
            s_sum += arr.sum()
            s_sq_sum += (arr ** 2).sum()
            count += arr.size
        mean = float(s_sum / count)
        var = float(s_sq_sum / count - mean ** 2)
        std = float(np.sqrt(var) if var > 0 else 1.0)
        scaler = {"mean": mean, "std": std}
        joblib.dump(scaler, scaler_file)

    while not Path(scaler_file).exists():
        tf.print("Waiting for chief to compute scaler...")
        tf.sleep(1)

    scaler = joblib.load(scaler_file)

    train_paths = df.iloc[train_idx]["npy_path"].astype(str).tolist()
    val_paths = df.iloc[val_idx]["npy_path"].astype(str).tolist()
    train_labels = [label_to_idx[l] for l in df.iloc[train_idx]["label"]]
    val_labels = [label_to_idx[l] for l in df.iloc[val_idx]["label"]]

    return train_paths, train_labels, val_paths, val_labels, train_idx, val_idx, test_idx, label_to_idx, scaler


def load_dataset(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found at {csv_path}")
    df = pd.read_csv(csv_path)
    required_cols = {"window_id", "filename", "label", "npy_path"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    return df


def song_wise_split(df: pd.DataFrame, test_size=0.2, val_from_test=0.5):
    df = df.copy()
    df["song_id"] = df["filename"].apply(lambda x: str(x).split("_part")[0])

    X_idx = np.arange(len(df))
    y = df["label"].values
    groups = df["song_id"].values

    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
    train_idx, temp_idx = next(gss.split(X_idx, y, groups=groups))

    temp_y = y[temp_idx]
    sss = StratifiedShuffleSplit(n_splits=1, test_size=val_from_test, random_state=42)
    val_rel_idx, test_rel_idx = next(sss.split(temp_idx.reshape(-1, 1), temp_y))

    val_idx = temp_idx[val_rel_idx]
    test_idx = temp_idx[test_rel_idx]

    return train_idx, val_idx, test_idx


# ----------------------- CNN Model -----------------------

def build_cnn(
        input_shape: tuple,
        num_classes: int,
        filters=(32, 64, 128),
        kernel_size=(3, 3),
        dense_units=256,
        dropout_rate=0.5,
        learning_rate=1e-3
) -> tf.keras.Model:
    model = Sequential()
    for i, f in enumerate(filters):
        if i == 0:
            model.add(Conv2D(f, kernel_size, activation="relu", padding="same", input_shape=input_shape))
        else:
            model.add(Conv2D(f, kernel_size, activation="relu", padding="same"))
        model.add(BatchNormalization())
        model.add(MaxPooling2D((2, 2)))
    model.add(Flatten())
    model.add(Dense(dense_units, activation="relu"))
    model.add(Dropout(dropout_rate))
    model.add(Dense(num_classes, activation="softmax"))

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

    model.compile(
        optimizer=optimizer,
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


# ----------------------- Dataset Generator -----------------------


def load_npy(path, input_shape):
    data = np.load(path.decode())["input"].astype(np.float32)
    while data.ndim > len(input_shape):
        data = np.squeeze(data, axis=0)
    while data.ndim < len(input_shape):
        data = np.expand_dims(data, axis=-1)
    data = data.reshape(input_shape)
    return data


def make_tf_dataset(paths, labels, input_shape, num_classes, batch_size, shuffle):
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(paths), seed=42)

    def _map_fn(path, label):
        x = tf.numpy_function(load_npy, [path, input_shape], tf.float32)
        x.set_shape(input_shape)
        y = tf.one_hot(tf.cast(label, tf.int32), depth=num_classes)
        y = tf.cast(y, tf.float32)
        return x, y

    ds = ds.map(_map_fn, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(batch_size, drop_remainder=True)
    ds = ds.prefetch(tf.data.AUTOTUNE)
    return ds


# ----------------------- Training Pipeline -----------------------


def is_chief():
    tf_config = json.loads(os.environ.get("TF_CONFIG", "{}"))
    task = tf_config.get("task", {})
    return task.get("type") == "worker" and task.get("index") == 0


def train_model(
        csv_path=CNN_OUTPUT_CSV,
        batch_size=128,
        epochs=100,
        test_size=0.2,
        val_from_test=0.5,
        disabled_labels=None,
        downsampling=True,
        model_config=None
):
    global _labels

    train_paths, train_labels, val_paths, val_labels, train_idx, val_idx, test_idx, label_to_idx, scaler = \
        prepare_dataset(
            csv_path=Path(csv_path),
            disabled_labels=disabled_labels,
            downsampling=downsampling,
            test_size=test_size,
            val_from_test=val_from_test
        )

    _labels = list(label_to_idx.keys())
    num_classes = len(_labels)

    sample_arr = np.load(train_paths[0])["input"].astype(np.float32)
    while sample_arr.ndim > 3:
        sample_arr = sample_arr.squeeze(0)
    if sample_arr.ndim == 2:
        sample_arr = sample_arr[..., np.newaxis]
    input_shape = sample_arr.shape

    train_ds = make_tf_dataset(train_paths, train_labels, input_shape, num_classes, batch_size, shuffle=True)
    val_ds = make_tf_dataset(val_paths, val_labels, input_shape, num_classes, batch_size, shuffle=False)

    options = tf.data.Options()
    options.experimental_distribute.auto_shard_policy = tf.data.experimental.AutoShardPolicy.DATA
    train_ds = train_ds.with_options(options)
    val_ds = val_ds.with_options(options)

    model = build_cnn(input_shape=input_shape, num_classes=num_classes, **(model_config or {}))

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=12, restore_best_weights=True)
    ]
    if is_chief():
        callbacks.append(tf.keras.callbacks.ModelCheckpoint(
            filepath=CNN_WEIGHTS_PATH,
            monitor="val_loss",
            save_best_only=True,
            save_weights_only=True
        ))

    effective_train_steps = max(1, len(train_paths) // batch_size)
    effective_val_steps = max(1, len(val_paths) // batch_size)

    print(f"Train samples: {len(train_paths)}")
    print(f"Val samples: {len(val_paths)}")
    print(f"Batch size: {batch_size}")
    print(f"Effective train steps: {effective_train_steps}")
    print(f"Effective val steps: {effective_val_steps}")

    model.fit(train_ds,
              validation_data=val_ds,
              epochs=epochs,
              steps_per_epoch=effective_train_steps,
              validation_steps=effective_val_steps,
              callbacks=callbacks,
              verbose=1)


# ----------------------- Inference -----------------------

def classify_audio(file_path: str, extractor) -> dict:
    global _model, _scaler, _labels
    if _model is None:
        _model = tf.keras.models.load_model(CNN_MODEL_PATH)
    if _scaler is None:
        _scaler = joblib.load(SCALER_PATH)
    if _labels is None:
        with open(CNN_LABELS_PATH) as f:
            _labels = json.load(f)

    patches = extractor.extract_features_from_file(file_path)
    if not patches:
        raise ValueError("No patches extracted")

    batch = np.asarray(patches, dtype=np.float32)

    if batch.ndim == 5 and batch.shape[1] == 1:
        batch = batch[:, 0]

    mean = _scaler["mean"]
    std = _scaler["std"]

    batch = (batch - mean) / (std + 1e-8)

    probs = _model.predict(batch, verbose=0)
    avg = probs.mean(axis=0)

    pairs = sorted(
        zip(_labels, avg.tolist()),
        key=lambda x: x[1],
        reverse=True
    )

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
