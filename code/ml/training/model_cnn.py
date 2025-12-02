import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import GroupShuffleSplit
from tensorflow.keras import layers, models, regularizers
from tensorflow.keras.callbacks import EarlyStopping
import coremltools as ct

from config.paths import CNN_MODEL_PATH, SCALER_PATH, CNN_LABELS_PATH, CNN_OUTPUT_CSV, COREML_PATH

_model = None
_scaler = None

strategy = tf.distribute.experimental.CentralStorageStrategy()

def make_tf_dataset_cpu(df, indices, label_to_idx, scaler, batch_size=256, shuffle=True):
    arrays, labels = [], []

    for i in indices:
        arr = np.load(df.iloc[i]["npy_path"])["input"].astype(np.float32)
        while arr.ndim > 3:
            arr = arr.squeeze(0)
        if arr.ndim == 2:
            arr = arr[..., np.newaxis]
        arr = (arr - scaler["mean"]) / (scaler["std"] + 1e-8)
        arrays.append(arr)
        labels.append(label_to_idx[df.iloc[i]["label"]])

    arrays = np.stack(arrays, axis=0)
    labels = tf.one_hot(np.array(labels, dtype=np.int32), depth=len(label_to_idx))

    ds = tf.data.Dataset.from_tensor_slices((arrays, labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(arrays), seed=42)
    # Parallelize preprocessing and prefetch
    ds = ds.map(lambda x, y: (tf.identity(x), tf.identity(y)), num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(batch_size)
    ds = ds.prefetch(tf.data.AUTOTUNE)
    return ds


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


def song_wise_split(df: pd.DataFrame, test_size=0.2, val_from_test=0.5) -> tuple:
    df = df.copy()
    df["song_id"] = df["filename"].apply(lambda x: str(x).split("_part")[0])
    X_idx = np.arange(len(df))
    y = df["label"].values
    groups = df["song_id"].values

    gss1 = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
    train_idx, temp_idx = next(gss1.split(X_idx, y, groups=groups))

    temp_groups = groups[temp_idx]
    temp_y = y[temp_idx]
    gss2 = GroupShuffleSplit(n_splits=1, test_size=val_from_test, random_state=42)
    val_rel_idx, test_rel_idx = next(gss2.split(temp_idx, temp_y, groups=temp_groups))

    val_idx = temp_idx[val_rel_idx]
    test_idx = temp_idx[test_rel_idx]
    return train_idx, val_idx, test_idx


def compute_global_mean_std(npy_paths: list, sample_limit=5000) -> dict:
    if not npy_paths:
        raise ValueError("No npy paths provided")

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


# ----------------------- TensorFlow Dataset -----------------------

def make_tf_dataset(df, indices, label_to_idx, scaler, batch_size=256, shuffle=True):
    arrays, labels = [], []

    for i in indices:
        arr = np.load(df.iloc[i]["npy_path"])["input"].astype(np.float32)
        while arr.ndim > 3:
            arr = arr.squeeze(0)
        if arr.ndim == 2:
            arr = arr[..., np.newaxis]
        arr = (arr - scaler["mean"]) / (scaler["std"] + 1e-8)
        arrays.append(arr)
        labels.append(label_to_idx[df.iloc[i]["label"]])

    arrays = np.stack(arrays, axis=0)
    labels = tf.one_hot(np.array(labels, dtype=np.int32), depth=len(label_to_idx))

    ds = tf.data.Dataset.from_tensor_slices((arrays, labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(arrays), seed=42)
    return ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)


# ----------------------- Model -----------------------

def build_cnn(input_shape: tuple, num_classes: int) -> tf.keras.Model:
    inp = layers.Input(shape=input_shape)
    x = layers.Conv2D(32, 3, padding="same", activation="relu")(inp)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPool2D()(x)
    x = layers.Dropout(0.15)(x)

    x = layers.Conv2D(64, 3, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPool2D()(x)
    x = layers.Dropout(0.2)(x)

    x = layers.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPool2D()(x)
    x = layers.Dropout(0.25)(x)

    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation="relu", kernel_regularizer=regularizers.l2(1e-4))(x)
    x = layers.Dropout(0.4)(x)
    out = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inp, out)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-4),
                  loss="categorical_crossentropy",
                  metrics=["accuracy"])
    return model


# ----------------------- Training Pipeline -----------------------

def train_model(csv_path=CNN_OUTPUT_CSV, test_size=0.2, val_from_test=0.5,
                batch_size=32, epochs=100, disabled_labels=None) -> dict:
    df = load_dataset(Path(csv_path))
    if disabled_labels:
        df = df[~df["label"].isin(disabled_labels)]
        if df.empty:
            raise ValueError("All labels disabled removed the dataset")
    df = balanced_downsample(df)

    labels = sorted(df["label"].unique())
    label_to_idx = {l: i for i, l in enumerate(labels)}
    with open(CNN_LABELS_PATH, "w") as f:
        json.dump(labels, f)

    train_idx, val_idx, test_idx = song_wise_split(df, test_size, val_from_test)
    train_paths = df.iloc[train_idx]["npy_path"].tolist()
    scaler = compute_global_mean_std(train_paths, sample_limit=4000)
    joblib.dump(scaler, SCALER_PATH)

    sample_arr = np.load(train_paths[0])["input"].astype(np.float32)
    while sample_arr.ndim > 3:
        sample_arr = sample_arr.squeeze(0)
    if sample_arr.ndim == 2:
        sample_arr = sample_arr[..., np.newaxis]
    input_shape = sample_arr.shape

    train_ds = make_tf_dataset_cpu(df, train_idx, label_to_idx, scaler, batch_size=256, shuffle=True)
    val_ds = make_tf_dataset_cpu(df, val_idx, label_to_idx, scaler, batch_size=256, shuffle=False)
    test_ds = make_tf_dataset_cpu(df, test_idx, label_to_idx, scaler, batch_size=256, shuffle=False)

    with strategy.scope():
        model = build_cnn(input_shape, num_classes=len(labels))
        model.compile(
            optimizer=tf.keras.optimizers.Adam(1e-4),
            loss="categorical_crossentropy",
            metrics=["accuracy"]
        )

    stopper = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=12, restore_best_weights=True)
    history = model.fit(train_ds, validation_data=val_ds, epochs=epochs, callbacks=[stopper], verbose=1)

    model.save(CNN_MODEL_PATH)
    loss, acc = model.evaluate(test_ds, verbose=0)

    cm = ct.convert(model, source="tensorflow", inputs=[ct.TensorType(shape=(1,) + input_shape)])
    cm.save(COREML_PATH)

    print(f"Test Loss: {loss:.4f}, Test Accuracy: {acc:.4f}")

    return {
        "loss": loss,
        "accuracy": acc,
        "labels": labels,
        "input_shape": input_shape,
        "history": history.history,
        "X_train": df.iloc[train_idx],
        "y_train": [label_to_idx[l] for l in df.iloc[train_idx]["label"]],
        "X_val": df.iloc[val_idx],
        "y_val": [label_to_idx[l] for l in df.iloc[val_idx]["label"]],
        "X_test": df.iloc[test_idx],
        "y_test": [label_to_idx[l] for l in df.iloc[test_idx]["label"]]
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
