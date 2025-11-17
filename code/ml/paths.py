from pathlib import Path

# Base directory for all storage
BASE_DIR = Path("/app/song-storage")

# Model files
MODEL_PATH = BASE_DIR / "model.keras"
SCALER_PATH = BASE_DIR / "scaler.pkl"
LABELS_PATH = BASE_DIR / "label_order.json"
FEATURES_CSV = BASE_DIR / "features.csv"
COREML_PATH = BASE_DIR / "model.mlmodel"

# Dataset paths
SONGS_DIR = BASE_DIR / "songs"
SNIPPETS_DIR = SONGS_DIR / "snippets"

# Default dataset output
DEFAULT_FEATURES_CSV = FEATURES_CSV
