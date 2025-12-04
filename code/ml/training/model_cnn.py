import json
import os
from pathlib import Path

import coremltools as ct
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import GroupShuffleSplit, StratifiedShuffleSplit
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.models import Sequential

from config.paths import CNN_MODEL_PATH, SCALER_PATH, CNN_LABELS_PATH, CNN_OUTPUT_CSV, COREML_PATH, CNN_DATASET_PATH

# ----------------------- Threading / CPU Optimization -----------------------
tf.config.threading.set_intra_op_parallelism_threads(os.cpu_count())
tf.config.threading.set_inter_op_parallelism_threads(os.cpu_count())
os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())
os.environ["MKL_NUM_THREADS"] = str(os.cpu_count())

_model = None
_scaler = None


# ----------------------- Dataset Utilities -----------------------

def load_dataset(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found at {csv_path}")
    df = pd.read_csv(csv_path)
    required_cols = {"window_id", "filename", "label", "npy_path"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    return df


def balanced_downsample(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["label"].value_counts()
    min_count = counts.min()
    return (
        pd.concat([df[df["label"] == lbl].sample(min_count, random_state=42)
                   for lbl in counts.index])
        .sample(frac=1.0, random_state=42)
        .reset_index(drop=True)
    )


def song_wise_split(df: pd.DataFrame, test_size=0.2, val_from_test=0.5):
    df = df.copy()
    df["song_id"] = df["filename"].apply(lambda x: str(x).split("_part")[0])

    X_idx = np.arange(len(df))
    y = df["label"].values
    groups = df["song_id"].values

    # First split: train vs temp (val+test)
    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
    train_idx, temp_idx = next(gss.split(X_idx, y, groups=groups))

    # Second split: val vs test, maintain stratification
    temp_y = y[temp_idx]
    temp_groups = groups[temp_idx]
    sss = StratifiedShuffleSplit(n_splits=1, test_size=val_from_test, random_state=42)
    val_rel_idx, test_rel_idx = next(sss.split(temp_idx.reshape(-1, 1), temp_y))

    val_idx = temp_idx[val_rel_idx]
    test_idx = temp_idx[test_rel_idx]

    return train_idx, val_idx, test_idx


def compute_global_mean_std(npy_paths: list, sample_limit=5000) -> dict:
    if len(npy_paths) > sample_limit:
        rng = np.random.default_rng(42)
        npy_paths = [npy_paths[i] for i in rng.choice(len(npy_paths), sample_limit, replace=False)]
    s_sum, s_sq_sum, count = 0.0, 0.0, 0
    for p in npy_paths:
        arr = np.load(p)["input"].astype(np.float32).ravel()
        s_sum += arr.sum()
        s_sq_sum += (arr ** 2).sum()
        count += arr.size
    mean = float(s_sum / count)
    var = float(s_sq_sum / count - mean ** 2)
    std = float(np.sqrt(var) if var > 0 else 1.0)
    return {"mean": mean, "std": std}


# ----------------------- CNN Model -----------------------

def build_cnn(input_shape: tuple, num_classes: int) -> tf.keras.Model:
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=input_shape),
        BatchNormalization(),
        MaxPooling2D((2, 2)),

        Conv2D(64, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),

        Conv2D(128, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),

        Flatten(),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model


# ----------------------- Dataset Generator -----------------------

def dataset_generator(indices, df, scaler, label_to_idx):
    for i in indices:
        arr = np.load(df.iloc[i]["npy_path"])["input"].astype(np.float32)
        while arr.ndim > 3:
            arr = arr.squeeze(0)
        if arr.ndim == 2:
            arr = arr[..., np.newaxis]
        arr = (arr - scaler["mean"]) / (scaler["std"] + 1e-8)
        label = label_to_idx[df.iloc[i]["label"]]
        yield arr, label


def make_tf_dataset(indices, df, scaler, label_to_idx, input_shape, num_classes, batch_size=64, shuffle=True):
    ds = tf.data.Dataset.from_generator(
        lambda: dataset_generator(indices, df, scaler, label_to_idx),
        output_signature=(
            tf.TensorSpec(shape=input_shape, dtype=tf.float32),
            tf.TensorSpec(shape=(), dtype=tf.int32)
        )
    )
    ds = ds.map(lambda x, y: (x, tf.one_hot(y, depth=num_classes)), num_parallel_calls=tf.data.AUTOTUNE)
    if shuffle:
        ds = ds.shuffle(buffer_size=min(2048, len(indices)), seed=42)
    ds = ds.batch(batch_size)
    ds = ds.prefetch(tf.data.AUTOTUNE)
    return ds


# ----------------------- Training Pipeline -----------------------

def collect_dataset(tf_dataset):
    X_list = []
    y_list = []
    for X_batch, y_batch in tf_dataset:
        X_list.append(X_batch.numpy())
        y_list.append(y_batch.numpy())

    X_full = np.concatenate(X_list, axis=0)
    y_full = np.concatenate(y_list, axis=0)
    return X_full, y_full


def train_model(
        csv_path=CNN_OUTPUT_CSV,
        batch_size=64,
        epochs=100,
        test_size=0.2,
        val_from_test=0.5,
        disabled_labels=None,
        downsampling=True
):
    df = load_dataset(Path(csv_path))

    if disabled_labels:
        df = df[~df["label"].isin(disabled_labels)]
        if df.empty:
            raise ValueError("All labels removed by disabled_labels")

    if downsampling:
        df = balanced_downsample(df)

    labels = sorted(df["label"].unique())
    label_to_idx = {l: i for i, l in enumerate(labels)}

    with open(CNN_LABELS_PATH, "w") as f:
        json.dump(labels, f)

    train_idx, val_idx, test_idx = song_wise_split(df, test_size, val_from_test)

    scaler = compute_global_mean_std(
        df.iloc[train_idx]["npy_path"].tolist(),
        sample_limit=4000
    )
    joblib.dump(scaler, SCALER_PATH)

    sample_arr = np.load(df.iloc[train_idx[0]]["npy_path"])["input"].astype(np.float32)

    while sample_arr.ndim > 3:
        sample_arr = sample_arr.squeeze(0)

    if sample_arr.ndim == 2:
        sample_arr = sample_arr[..., np.newaxis]

    input_shape = sample_arr.shape
    num_classes = len(labels)

    train_ds = make_tf_dataset(
        train_idx, df, scaler, label_to_idx,
        input_shape, num_classes,
        batch_size=batch_size, shuffle=True
    )

    val_ds = make_tf_dataset(
        val_idx, df, scaler, label_to_idx,
        input_shape, num_classes,
        batch_size=batch_size, shuffle=False
    )

    test_ds = make_tf_dataset(
        test_idx, df, scaler, label_to_idx,
        input_shape, num_classes,
        batch_size=batch_size, shuffle=False
    )

    X_train, y_train = collect_dataset(train_ds)
    X_val, y_val = collect_dataset(val_ds)
    X_test, y_test = collect_dataset(test_ds)

    np.savez(CNN_DATASET_PATH + "/train_data.npz", X=X_train, y=y_train)
    np.savez(CNN_DATASET_PATH + "/val_data.npz", X=X_val, y=y_val)
    np.savez(CNN_DATASET_PATH + "/test_data.npz", X=X_test, y=y_test)

    model = build_cnn(input_shape, num_classes)
    stopper = EarlyStopping(monitor="val_loss", patience=12, restore_best_weights=True)

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=[stopper],
        verbose=1
    )

    model.save(CNN_MODEL_PATH)

    loss, acc = model.evaluate(test_ds, verbose=0)

    cm = ct.convert(
        model,
        source="tensorflow",
        inputs=[ct.TensorType(shape=(1,) + input_shape)]
    )
    cm.save(COREML_PATH)

    print("Test Loss: {:.4f}, Test Accuracy: {:.4f}".format(loss, acc))

    return {
        "loss": float(loss),
        "accuracy": float(acc),
        "labels": labels,
        "input_shape": input_shape,
        "history": history.history,
        "train_idx": train_idx,
        "val_idx": val_idx,
        "test_idx": test_idx
    }


# ----------------------- Inference -----------------------

def classify_audio(file_path: str, extractor, top_k=5) -> dict:
    global _model, _scaler
    if _model is None:
        _model = tf.keras.models.load_model(CNN_MODEL_PATH)
    if _scaler is None:
        _scaler = joblib.load(SCALER_PATH)

    patches = extractor.extract_features_from_file(file_path)
    if not patches:
        raise ValueError("No patches extracted")

    arrs = []
    for p in patches:
        a = p.astype(np.float32)
        if a.ndim == 4 and a.shape[0] == 1:
            a = a[0]
        a = (a - _scaler["mean"]) / (_scaler["std"] + 1e-8)
        arrs.append(a)

    batch = np.stack(arrs, axis=0)
    probs = _model.predict(batch, verbose=0)
    avg = probs.mean(axis=0)

    with open(CNN_LABELS_PATH) as f:
        labels = json.load(f)
    pairs = sorted(zip(labels, avg.tolist()), key=lambda x: x[1], reverse=True)

    return {
        "predictions": [{"danceName": l, "confidence": float(f"{c:.6f}")} for l, c in pairs[:top_k]],
        "all": [{"danceName": l, "confidence": float(f"{c:.6f}")} for l, c in pairs]
    }


def load_model():
    global _model, _scaler
    _model = tf.keras.models.load_model(CNN_MODEL_PATH)
    _scaler = joblib.load(SCALER_PATH)
