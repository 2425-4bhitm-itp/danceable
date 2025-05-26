import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import coremltools as ct
import pandas as pd
import re

model = None

def train():
    print('Training...')

    # Load dataset
    df = pd.read_csv("/app/song-storage/features.csv")

    # Separate features and labels
    feature_columns = [col for col in df.columns if col not in ["filename", "label"]]
    X = df[feature_columns].values
    y = df["label"].values

    # Normalize features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Convert labels to one-hot encoding
    unique_labels = sorted(df["label"].unique())
    label_to_index = {label: idx for idx, label in enumerate(unique_labels)}
    y = to_categorical([label_to_index[label] for label in y], num_classes=len(unique_labels))

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Build the TensorFlow model
    model = Sequential([
        Input(shape=(X_train.shape[1],)),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(len(unique_labels), activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(X_train, y_train, validation_split=0.2, epochs=60, batch_size=32)

    # Save the model in TensorFlow format
    model.save("/app/song-storage/model.keras")

    # Reload the model before Core ML conversion
    reloaded_model = tf.keras.models.load_model("/app/song-storage/model.keras")

    # Create a concrete function for Core ML conversion
    input_spec = tf.TensorSpec([None, X_train.shape[1]], tf.float32)
    reloaded_model_func = tf.function(reloaded_model).get_concrete_function(input_spec)

    # Convert the TensorFlow model to Core ML format
    coreml_model = ct.convert(reloaded_model_func, source="tensorflow", minimum_deployment_target=ct.target.iOS14)

    # Save the Core ML model
    coreml_model.save("/app/song-storage/model.mlmodel")

    return model.evaluate(X_test, y_test, verbose=0)

def classify_audio(file_path, extractor):
    global model
    if model is not None:
        features = extractor.extract_features_from_file(file_path)

        feature_vector = features.flatten().reshape(1, -1)

        # Load the model if not already loaded
        if not isinstance(model, tf.keras.Model):
            model = tf.keras.models.load_model("/app/song-storage/model.h5")

        probabilities = model.predict(feature_vector)[0]
        dance_styles = sorted(model.output_names)
        predictions = sorted(zip(dance_styles, probabilities), key=lambda x: x[1], reverse=True)

        prediction_dtos = [
            {
                "danceName": dance,
                "confidence": float(f"{confidence:.6f}"),
                "speedCategory": "slow"
            }
            for dance, confidence in predictions
        ]
        return prediction_dtos

    return []

def load_model():
    global model
    model = tf.keras.models.load_model("/app/song-storage/model.keras")
    print("Model loaded from .keras file")