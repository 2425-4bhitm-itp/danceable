import json
from pathlib import Path

import coremltools as ct
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupShuffleSplit
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.regularizers import l2
from tensorflow.keras.utils import to_categorical

from config.paths import MODEL_PATH, SCALER_PATH, LABELS_PATH, FEATURES_CSV, COREML_PATH

model = None
scaler = None


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------

def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Feature CSV not found at {path}")
    df = pd.read_csv(path)
    if "label" not in df.columns:
        raise ValueError("CSV missing 'label' column")
    return df

def balanced_downsample(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["label"].value_counts()
    min_count = counts.min()
    frames = []
    for label in counts.index:
        subset = df[df["label"] == label]
        frames.append(subset.sample(n=min_count, random_state=42))
    return pd.concat(frames).sample(frac=1.0, random_state=42).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Feature Handling
# ---------------------------------------------------------------------------

def build_feature_groups(df: pd.DataFrame) -> dict:
    feature_cols = [c for c in df.columns if c not in ["filename", "label"]]
    return {
        "mfcc": [c for c in feature_cols if c.startswith("mfcc_")],
        "chroma": [c for c in feature_cols if c.startswith("chroma_")],
        "mel": [c for c in feature_cols if c.startswith("mel_")],
        "contrast": [c for c in feature_cols if c.startswith("contrast_")],
        "tonnetz": [c for c in feature_cols if c.startswith("tonnetz_")],
        "tempogram": [c for c in feature_cols if c.startswith("tempogram_")],
        "rms": [c for c in feature_cols if c.startswith("rms_")],
        "spectral_flux": [c for c in feature_cols if c.startswith("spectral_flux_")],
        "onset": [c for c in feature_cols if c.startswith("onset_strength_")],
        "tempo": [c for c in feature_cols if c == "tempo_bpm"],
    }


def select_columns(groups: dict, selected: list | None) -> list:
    if selected is None:
        selected = [g for g in groups if groups[g]]
    invalid = [g for g in selected if g not in groups]
    if invalid:
        raise ValueError(f"Invalid feature groups: {invalid}")
    cols = []
    for name in selected:
        cols.extend(groups[name])
    if not cols:
        raise ValueError("No feature columns available for training")
    return cols

def song_wise_split(df: pd.DataFrame, test_size, val_from_test, filename_col):
    df["song_id"] = df[filename_col].apply(lambda x: x.split("_part")[0])

    X = df.drop(columns=["label", filename_col, "song_id"]).values
    y = df["label"].values
    groups = df["song_id"].values

    gss1 = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
    train_idx, temp_idx = next(gss1.split(X, y, groups=groups))

    X_train, X_temp = X[train_idx], X[temp_idx]
    y_train, y_temp = y[train_idx], y[temp_idx]
    groups_temp = groups[temp_idx]

    gss2 = GroupShuffleSplit(n_splits=1, test_size=val_from_test, random_state=42)
    val_idx, test_idx = next(gss2.split(X_temp, y_temp, groups=groups_temp))

    X_val, X_test = X_temp[val_idx], X_temp[test_idx]
    y_val, y_test = y_temp[val_idx], y_temp[test_idx]

    return X_train, X_val, X_test, y_train, y_val, y_test

# ---------------------------------------------------------------------------
# Scaling
# ---------------------------------------------------------------------------

def scale_groups(df: pd.DataFrame, groups: dict, selected: list) -> pd.DataFrame:
    for group in selected:
        cols = groups[group]
        if cols:
            scaler_group = StandardScaler()
            df[cols] = scaler_group.fit_transform(df[cols])
    return df


def apply_global_scaling(X: np.ndarray, cols: list) -> tuple:
    global_scaler = StandardScaler()
    X_scaled = global_scaler.fit_transform(X)
    joblib.dump({"scaler": global_scaler, "features": cols}, SCALER_PATH)
    return X_scaled, global_scaler


# ---------------------------------------------------------------------------
# Label Encoding
# ---------------------------------------------------------------------------

def encode_labels(labels: np.ndarray) -> tuple:
    unique = sorted(np.unique(labels))
    mapping = {label: idx for idx, label in enumerate(unique)}
    encoded = to_categorical([mapping[l] for l in labels], num_classes=len(unique))
    with open(LABELS_PATH, "w") as f:
        json.dump(unique, f)
    return encoded, unique

def encode_split(y_split, label_mapping, unique_labels):
    return to_categorical([label_mapping[l] for l in y_split], num_classes=len(unique_labels))

# ---------------------------------------------------------------------------
# Model Construction
# ---------------------------------------------------------------------------

def build_model(input_dim: int, output_dim: int) -> Sequential:
    m = Sequential()
    m.add(Input(shape=(input_dim,)))
    m.add(Dense(128, activation="relu", kernel_regularizer=l2(0.01)))
    m.add(Dropout(0.5))
    m.add(Dense(64, activation="relu", kernel_regularizer=l2(0.01)))
    m.add(Dropout(0.5))
    m.add(Dense(output_dim, activation="softmax"))
    m.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    return m


# ---------------------------------------------------------------------------
# Training Pipeline
# ---------------------------------------------------------------------------

def train(
        selected_features=None,
        disabled_labels=None,
        test_size=0.2,
        val_from_test=0.5
):
    df = load_dataset(FEATURES_CSV)

    if disabled_labels:
        df = df[~df["label"].isin(disabled_labels)]
        if df.empty:
            raise ValueError("Disabled labels removed the whole dataset")

    df = balanced_downsample(df)
    print(df["label"].value_counts())
    groups = build_feature_groups(df)
    selected_cols = select_columns(groups, selected_features)
    df = scale_groups(df, groups, selected_features or list(groups.keys()))

    X_train, X_val, X_test, y_train_raw, y_val_raw, y_test_raw = song_wise_split(df, test_size, val_from_test, "filename")

    y_all_encoded, unique_labels = encode_labels(df["label"].values)
    label_mapping = {label: idx for idx, label in enumerate(unique_labels)}

    y_train = encode_split(y_train_raw, label_mapping, unique_labels)
    y_val = encode_split(y_val_raw, label_mapping, unique_labels)
    y_test = encode_split(y_test_raw, label_mapping, unique_labels)

    m = build_model(X_train.shape[1], len(unique_labels))
    stopper = EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True)

    m.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=32,
        callbacks=[stopper],
        verbose=1,
    )

    m.save(MODEL_PATH)

    loss, acc = m.evaluate(X_test, y_test, verbose=0)

    cm = ct.convert(m, source="tensorflow", inputs=[ct.TensorType(shape=(1, X_train.shape[1]))])
    cm.save(COREML_PATH)

    return {
        "loss": loss,
        "accuracy": acc,
        "used_features": selected_cols,
        "used_labels": unique_labels,
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
        "X_test": X_test,
        "y_test": y_test,
    }

# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_audio(file_path, extractor):
    global model, scaler

    if model is None:
        model = tf.keras.models.load_model(MODEL_PATH)
    if scaler is None:
        scaler = joblib.load(SCALER_PATH)

    features = extractor.extract_features_from_file(file_path)
    vector = np.array(list(features.values()), dtype=np.float32).reshape(1, -1)
    vector = scaler["scaler"].transform(vector)

    with open(LABELS_PATH) as f:
        labels = json.load(f)

    probs = model.predict(vector, verbose=0)[0]
    pairs = sorted(zip(labels, probs), key=lambda x: x[1], reverse=True)

    return {
        "predictions": [
            {"danceName": label, "confidence": float(f"{conf:.6f}")} for label, conf in pairs
        ]
    }


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_model():
    global model, scaler
    model = tf.keras.models.load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
