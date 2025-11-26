from pathlib import Path

# Base directory for all storage
BASE_DIR = Path("/app/song-storage")
BASE_MODEL_DIR = Path("/opt/model")

# Model files
MODEL_PATH = BASE_MODEL_DIR / "model.keras"
SCALER_PATH = BASE_MODEL_DIR / "scaler.pkl"
LABELS_PATH = BASE_MODEL_DIR / "label_order.json"
COREML_PATH = BASE_MODEL_DIR / "model.mlmodel"

# Dataset paths
FEATURES_CSV = BASE_DIR / "features.csv"
SONGS_DIR = BASE_DIR / "songs"
SNIPPETS_DIR = SONGS_DIR / "snippets"