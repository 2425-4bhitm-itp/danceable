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
            df = pd.read_csv(self.output_csv)
            return set(df.loc[df["npy_path"].map(os.path.exists), "window_id"].astype(str))
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

    def save_csv(self, new_rows):
        csv_file = output_csv
        fieldnames = ["window_id", "filename", "label", "npy_path"]

        file_exists = csv_file.exists()

        with open(csv_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for row in new_rows:
                writer.writerow(row)

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
        if arr.ndim == 3 and arr.shape[0] <= 6:  # assume 6 features max
            arr = np.transpose(arr, (1, 2, 0))  # (C,H,W) -> (H,W,C)
        elif arr.ndim == 2:
            arr = arr[..., np.newaxis]
        elif arr.ndim != 3:
            raise ValueError(f"Unexpected tensor shape: {arr.shape}")
        return arr

    def clear_files(self):
        if self.output_csv.exists():
            self.output_csv.unlink()
        for npz_file in self.output_dir.glob("*.npz"):
            npz_file.unlink()

    def merge_csv_files(self, csv_paths):
        if not csv_paths:
            return

        with open(self.csv_path, "w", newline="", encoding="utf-8") as out_f:
            writer = None

            for path in csv_paths:
                with open(path, "r", newline="", encoding="utf-8") as in_f:
                    reader = csv.DictReader(in_f)
                    if writer is None:
                        writer = csv.DictWriter(out_f, fieldnames=reader.fieldnames)
                        writer.writeheader()
                    writer.writerows(reader)
