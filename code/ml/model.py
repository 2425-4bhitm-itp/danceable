import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import coremltools as ct
import joblib

model = None

def train():
    global model
    print('Training...')

    # Load dataset
    df = pd.read_csv("/app/song-storage/features.csv")

    # Separate features and labels
    X = df.drop(columns=["filename", "label"]).values
    y = df["label"].values

    # Split into training & test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.2f}")

    # Save model as joblib (optional)
    joblib.dump(model, "/app/song-storage/model.joblib")

    # Convert to Core ML
    coreml_model = ct.converters.sklearn.convert(model)

    # Save Core ML model
    coreml_model.save("/app/song-storage/model.mlmodel")

def classify_audio(file_path, extractor):
    global model
    features = extractor.extract_features_from_file(file_path).reshape(1, -1)
    predictions = None
    if model is not None:
        probabilities = model.predict_proba(features)[0]
        dance_styles = model.classes_
        predictions = sorted(zip(dance_styles, probabilities), key=lambda x: x[1], reverse=True)
    return predictions

def load_model():
    global model
    model = joblib.load("/app/song-storage/model.joblib")
    print("model loaded")