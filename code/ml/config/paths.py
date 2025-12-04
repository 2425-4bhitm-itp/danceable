from pathlib import Path

# Base directory for all storage
BASE_DIR = Path("/app/song-storage")
BASE_MODEL_DIR = Path("/opt/model")

# Model files
MODEL_PATH = BASE_MODEL_DIR / "model.keras"
SCALER_PATH = BASE_MODEL_DIR / "scaler.pkl"
LABELS_PATH = BASE_MODEL_DIR / "label_order.json"
COREML_PATH = BASE_MODEL_DIR / "model.mlmodel"

# CNN-specific model paths
CNN_MODEL_PATH = BASE_MODEL_DIR / "model_cnn.keras"
CNN_LABELS_PATH = BASE_MODEL_DIR / "label_order_cnn.json"

# Directory where spectrogram tensors are stored for CNN training
CNN_TRAIN_DATA_DIR = BASE_DIR / "cnn_tensors"
CNN_OUTPUT_CSV = BASE_DIR / "cnn_features.csv"
CNN_DATASET_PATH = BASE_DIR / "dataset"

# Dataset paths
FEATURES_CSV = BASE_DIR / "features.csv"
SONGS_DIR = BASE_DIR / "songs"
SNIPPETS_DIR = SONGS_DIR / "snippets"
EVALUATION_RESULTS_DIR = BASE_DIR / "evaluation_results"