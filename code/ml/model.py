import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import coremltools as ct
import joblib
import re
import numpy as np

model = None

def train():
    global model
    print('Training...')

    # Load dataset
    df = pd.read_csv("/app/song-storage/features.csv")

    # Extract song name by removing the last "X_partX.wav" section using regex
    df['song_name'] = df['filename'].apply(lambda x: re.sub(r'\d+_part\d+\.wav$', '', x))

    # Group by song name to ensure all segments from a song are treated together
    grouped = df.groupby('song_name')

    # Create separate lists for training and testing songs
    song_names = list(grouped.groups.keys())
    train_songs, test_songs = train_test_split(song_names, test_size=0.2, random_state=42)

    # Create new DataFrames for training and testing
    train_df = df[df['song_name'].isin(train_songs)]
    test_df = df[df['song_name'].isin(test_songs)]

    # Further split the training data into training and validation sets
    train_songs, val_songs = train_test_split(train_songs, test_size=0.2, random_state=42)
    train_df = df[df['song_name'].isin(train_songs)]
    val_df = df[df['song_name'].isin(val_songs)]

    # Separate features and labels
    feature_columns = [col for col in df.columns if col not in ["filename", "label", "song_name"]]
    X_train, y_train = train_df[feature_columns].values, train_df["label"].values
    X_val, y_val = val_df[feature_columns].values, val_df["label"].values
    X_test, y_test = test_df[feature_columns].values, test_df["label"].values

    # Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model on the validation set
    y_val_pred = model.predict(X_val)
    val_accuracy = accuracy_score(y_val, y_val_pred)

    # Evaluate the model on the test set
    y_test_pred = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_test_pred)

    # Save model as joblib (optional)
    joblib.dump(model, "/app/song-storage/model.joblib")

    # Convert to Core ML
    coreml_model = ct.converters.sklearn.convert(model)

    # Save Core ML model
    coreml_model.save("/app/song-storage/model.mlmodel")

    return test_accuracy, val_accuracy

def classify_audio(file_path, extractor):
    global model
    if model is not None:
        features = extractor.extract_features_from_file(file_path)

        feature_vector = [value for key in sorted(features.keys()) for value in features[key]]
        feature_vector = np.array(feature_vector).reshape(1, -1)

        probabilities = model.predict_proba(feature_vector)[0]
        dance_styles = model.classes_
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
    model = joblib.load("/app/song-storage/model.joblib")
    print("model loaded")