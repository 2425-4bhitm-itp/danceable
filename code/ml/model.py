import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import coremltools as ct
import pandas as pd
import joblib
import json

model = None
scaler = None

MODEL_PATH = "/app/song-storage/model.keras"
SCALER_PATH = "/app/song-storage/scaler.pkl"
LABELS_PATH = "/app/song-storage/label_order.json"
COREML_PATH = "/app/song-storage/model.mlmodel"
FEATURES_CSV = "/app/song-storage/features.csv"


def train():
    global model, scaler
    print('Training...')

    df = pd.read_csv(FEATURES_CSV)
    feature_columns = [col for col in df.columns if col not in ["filename", "label"]]

    # Group definitions
    groups = {
        "mfcc": [col for col in feature_columns if col.startswith("mfcc_")],
        "chroma": [col for col in feature_columns if col.startswith("chroma_")],
        "mel": [col for col in feature_columns if col.startswith("mel_")],
        "contrast": [col for col in feature_columns if col.startswith("contrast_")],
        "tonnetz": [col for col in feature_columns if col.startswith("tonnetz_")],
    }

    # Group-wise scaling
    for group, cols in groups.items():
        scaler = StandardScaler()
        df[cols] = scaler.fit_transform(df[cols])
        print(f"Scaled group: {group} ({len(cols)} features)")

    # Combine all features
    X = df[feature_columns].values
    y = df["label"].values

    # Final overall scaling (important)
    scaler_global = StandardScaler()
    X = scaler_global.fit_transform(X)
    joblib.dump(scaler_global, SCALER_PATH)
    print("Global scaler saved.")

    # Label encoding
    unique_labels = sorted(df["label"].unique())
    label_to_index = {label: idx for idx, label in enumerate(unique_labels)}
    y = to_categorical([label_to_index[label] for label in y], num_classes=len(unique_labels))

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

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
    model.fit(X_train, y_train, validation_split=0.2, epochs=100, batch_size=32, callbacks=[early_stopping])

    model.save(MODEL_PATH)
    print("Model saved.")

    with open(LABELS_PATH, "w") as f:
        json.dump(unique_labels, f)
    print("Label order saved.")

    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"Evaluation - Loss: {loss:.4f}, Accuracy: {acc:.4f}")

    # Optional CoreML conversion
    # coreml_model = ct.convert(
    #     model,
    #     source="tensorflow",
    #     inputs=[ct.TensorType(shape=(1, X_train.shape[1]))]
    # )
    # coreml_model.save(COREML_PATH)

    return loss, acc

def classify_audio(file_path, extractor):
    global model, scaler

    try:
        if model is None or not isinstance(model, tf.keras.Model):
            model = tf.keras.models.load_model(MODEL_PATH)
            print("Model loaded.")

        if scaler is None:
            scaler = joblib.load(SCALER_PATH)
            print("Scaler loaded.")

        # Extract and preprocess features
        features = extractor.extract_features_from_file(file_path)
        feature_vector = features.flatten().reshape(1, -1)
        print("Raw feature shape:", feature_vector.shape)

        feature_vector = scaler.transform(feature_vector)
        print("Feature vector normalized.")

        # Load label order
        with open(LABELS_PATH, "r") as f:
            dance_styles = json.load(f)

        # Predict
        probabilities = model.predict(feature_vector)[0]
        predictions = sorted(zip(dance_styles, probabilities), key=lambda x: x[1], reverse=True)

        return {
            "predictions": [
                {
                    "danceName": dance,
                    "confidence": float(f"{confidence:.6f}"),
                    "speedCategory": "slow"
                }
                for dance, confidence in predictions
            ]
        }

    except Exception as e:
        print("Error during classification:", str(e))
        return {"error": str(e)}

def load_model():
    global model, scaler
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("Model and scaler loaded successfully.")
    except Exception as e:
        print("Failed to load model or scaler:", e)
