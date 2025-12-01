import os
import csv
import uuid
import numpy as np
import pandas as pd
from pathlib import Path
from config.paths import CNN_OUTPUT_CSV as output_csv, CNN_TRAIN_DATA_DIR as output_dir

class AudioDatasetCreatorCNN:
    def __init__(self, extractor):
        self.extractor = extractor
        self.output_csv = Path(output_csv)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_existing(self):
        if self.output_csv.exists() and self.output_csv.stat().st_size > 0:
            return set(pd.read_csv(self.output_csv)["window_id"].astype(str))
        return set()

    def process_folder(self, folder_path, label):
        folder_path = Path(folder_path)
        processed = self.load_existing()

        wav_files = [f for f in folder_path.iterdir() if f.suffix.lower() == ".wav"]
        rows = []

        for file_path in wav_files:
            patches = self.extractor.extract_features_from_file(str(file_path))
            for patch in patches:
                # ensure patch is (H,W,C)
                patch = self._ensure_hwc(patch)

                window_id = str(uuid.uuid4())
                save_path = self.output_dir / f"{window_id}.npz"
                np.savez(save_path, input=patch, label=label)

                rows.append({
                    "window_id": window_id,
                    "filename": file_path.name,
                    "label": label,
                    "npy_path": str(save_path),
                })

        self.save_csv(rows)

    def save_csv(self, rows):
        if not rows:
            return
        fieldnames = ["window_id", "filename", "label", "npy_path"]
        write_header = not self.output_csv.exists() or self.output_csv.stat().st_size == 0
        with open(self.output_csv, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(rows)

    def upload_single_file(self, file_path, label):
        patches = self.extractor.extract_features_from_file(file_path)
        rows = []
        for patch in patches:
            patch = self._ensure_hwc(patch)
            window_id = str(uuid.uuid4())
            save_path = self.output_dir / f"{window_id}.npz"
            np.savez(save_path, input=patch, label=label)
            rows.append({
                "window_id": window_id,
                "filename": os.path.basename(file_path),
                "label": label,
                "npy_path": str(save_path),
            })
        self.save_csv(rows)

    def store_tensor(self, tensor, label, filename=None):
        tensor = self._ensure_hwc(tensor)
        if filename is None:
            filename = f"{label}_{np.random.randint(1e6)}.npz"
        path = os.path.join(self.output_dir, filename)
        np.savez(path, input=tensor, label=label)

    @staticmethod
    def _ensure_hwc(arr):
        arr = np.asarray(arr, dtype=np.float32)
        if arr.ndim == 2:
            arr = arr[..., np.newaxis]
        elif arr.ndim == 4 and arr.shape[0] == 1:
            arr = arr[0]
        elif arr.ndim != 3:
            raise ValueError(f"Unexpected tensor shape: {arr.shape}")
        return arr
