import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2
from sklearn.preprocessing import StandardScaler
import pandas as pd
import joblib
import json
import os
import numpy as np
import coremltools as ct

model = None
scaler = None

MODEL_PATH = "/app/song-storage/model.keras"
SCALER_PATH = "/app/song-storage/scaler.pkl"
LABELS_PATH = "/app/song-storage/label_order.json"
COREML_PATH = "/app/song-storage/model.mlmodel"
FEATURES_CSV = "/app/song-storage/features.csv"
COREML_PATH = "/app/song-storage/model.mlmodel"

def train(selected_features=None, disabled_labels=None):
    global model, scaler
    print("Training...")

    if not os.path.exists(FEATURES_CSV):
        raise FileNotFoundError(f"Feature CSV not found at {FEATURES_CSV}")

    df = pd.read_csv(FEATURES_CSV)
    if "label" not in df.columns:
        raise ValueError("CSV missing 'label' column")

    if disabled_labels:
        print(f"Disabled labels: {disabled_labels}")
        before_count = len(df)

        df = df[~df["label"].isin(disabled_labels)]

        after_count = len(df)
        if len(df) == 0:
            raise ValueError("All rows removed. Disabled labels removed the whole dataset.")

        print(f"Removed {before_count - after_count} rows containing disabled labels")

    feature_columns = [col for col in df.columns if col not in ["filename", "label"]]

    groups = {
        "mfcc": [c for c in feature_columns if c.startswith("mfcc_")],
        "chroma": [c for c in feature_columns if c.startswith("chroma_")],
        "mel": [c for c in feature_columns if c.startswith("mel_")],
        "contrast": [c for c in feature_columns if c.startswith("contrast_")],
        "tonnetz": [c for c in feature_columns if c.startswith("tonnetz_")],
        "tempogram": [c for c in feature_columns if c.startswith("tempogram_")],
        "rms": [col for col in feature_columns if col.startswith("rms_")],
        "spectral_flux": [col for col in feature_columns if col.startswith("spectral_flux_")],
        "onset": [col for col in feature_columns if col.startswith("onset_strength_")],
        "tempo": [col for col in feature_columns if col == "tempo_bpm"]
    }

    # Select feature groups
    if selected_features is None:
        selected_features = [g for g in groups if len(groups[g]) > 0]
    else:
        invalid = [g for g in selected_features if g not in groups]
        if invalid:
            raise ValueError(f"Invalid feature group(s): {invalid}")

    selected_cols = []
    for feat in selected_features:
        if not groups[feat]:
            print(f"Warning: no columns found for group '{feat}'")
        selected_cols.extend(groups[feat])

    if not selected_cols:
        raise ValueError("No valid feature columns selected for training")

    print(f"Using feature groups: {', '.join(selected_features)}")
    print(f"Total features: {len(selected_cols)}")

    # Group-wise scaling
    for group in selected_features:
        cols = groups[group]
        if len(cols) > 0:
            scaler_group = StandardScaler()
            df[cols] = scaler_group.fit_transform(df[cols])
            print(f"Scaled group: {group} ({len(cols)} features)")

    # Prepare final X, y
    X = df[selected_cols].values
    y = df["label"].values

    # Global scaler
    scaler_global = StandardScaler()
    X = scaler_global.fit_transform(X)

    # Save scaler in new format
    joblib.dump(
        {
            "scaler": scaler_global,
            "features": selected_cols
        },
        SCALER_PATH
    )
    print("Global scaler saved (with feature list).")

    # Encode labels
    unique_labels = sorted(df["label"].unique())
    label_to_index = {label: idx for idx, label in enumerate(unique_labels)}
    y_encoded = to_categorical([label_to_index[label] for label in y], num_classes=len(unique_labels))

    # Split
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    # Model
    model = Sequential([
        Input(shape=(X_train.shape[1],)),
        Dense(128, activation='relu', kernel_regularizer=l2(0.01)),
        Dropout(0.5),
        Dense(64, activation='relu', kernel_regularizer=l2(0.01)),
        Dropout(0.5),
        Dense(len(unique_labels), activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    print("Starting model training...")
    model.fit(X_train, y_train, validation_split=0.2, epochs=100, batch_size=32, callbacks=[early_stopping], verbose=1)

    model.save(MODEL_PATH)
    print(f"Model saved at {MODEL_PATH}")

    with open(LABELS_PATH, "w") as f:
        json.dump(unique_labels, f)
    print(f"Label order saved at {LABELS_PATH}")

    # Evaluate
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"Evaluation — Loss: {loss:.4f}, Accuracy: {acc:.4f}")

    # Optional CoreML conversion
    coreml_model = ct.convert(
        model,
        source="tensorflow",
        inputs=[ct.TensorType(shape=(1, X_train.shape[1]))]
    )
    coreml_model.save(COREML_PATH)

    return {
        "loss": loss,
        "accuracy": acc,
        "used_features": selected_features,
        "used_labels": unique_labels,
        "X_test": X_test,
        "y_test": y_test,
        "X_train": X_train,
        "y_train": y_train
    }


def classify_audio(file_path, extractor):
    """
    Classify a single audio file using the trained model.
    """
    global model, scaler

    try:
        if model is None or not isinstance(model, tf.keras.Model):
            model = tf.keras.models.load_model(MODEL_PATH)
            print("Model loaded from file.")

        if scaler is None:
            scaler = joblib.load(SCALER_PATH)
            print("Scaler loaded from file.")

        # Extract and preprocess features
        features = extractor.extract_features_from_file(file_path)
        features_vector = np.array(list(features.values()), dtype=np.float32).reshape(1, -1)

        features_vector = scaler.transform(features_vector)

        with open(LABELS_PATH, "r") as f:
            labels = json.load(f)

        probabilities = model.predict(features_vector, verbose=0)[0]
        predictions = sorted(zip(labels, probabilities), key=lambda x: x[1], reverse=True)

        return {
            "predictions": [
                {
                    "danceName": label,
                    "confidence": float(f"{conf:.6f}")
                }
                for label, conf in predictions
            ]
        }

    except Exception as e:
        print("Error during classification:", e)
        return {"error": str(e)}


def load_model():
    global model, scaler
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("Model and scaler loaded successfully.")
    except Exception as e:
        print(f"Failed to load model or scaler: {e}")
