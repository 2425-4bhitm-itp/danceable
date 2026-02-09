import csv
import json
import os
import uuid
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, StratifiedShuffleSplit

from config.paths import (
    CNN_OUTPUT_CSV,
    CNN_TRAIN_DATA_DIR,
    CNN_DATASET_PATH,
    SCALER_PATH,
)


class AudioDatasetCreatorCNN:
    CSV_COLUMNS = ["window_id", "filename", "label", "npy_path"]

    def __init__(self, extractor):
        self.extractor = extractor
        self.output_csv = Path(CNN_OUTPUT_CSV)
        self.output_dir = Path(CNN_TRAIN_DATA_DIR)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)

    def clear_files(self) -> None:
        if self.output_dir.exists():
            for p in self.output_dir.glob("*.npz"):
                p.unlink()

        if self.output_csv.exists():
            self.output_csv.unlink()

    def load_existing(self) -> set[str]:
        if not self.output_csv.exists():
            return set()

        df = pd.read_csv(self.output_csv)
        if df.empty:
            return set()

        return set(df["filename"].astype(str))

    def save_csv(self) -> None:
        if not self.output_csv.exists():
            return

        df = pd.read_csv(self.output_csv)
        df.to_csv(self.output_csv, index=False)

    def load_existing_window_ids(self) -> set[str]:
        if not self.output_csv.exists():
            return set()

        df = pd.read_csv(self.output_csv)
        if df.empty:
            return set()

        return set(
            df.loc[df["npy_path"].map(os.path.exists), "window_id"].astype(str)
        )

    def process_folder(self, folder_path: str | Path, label: str) -> None:
        folder_path = Path(folder_path)
        existing_files = self.load_existing()

        rows = []

        for wav_path in folder_path.iterdir():
            if wav_path.suffix.lower() != ".wav":
                continue

            if wav_path.name in existing_files:
                continue

            patches = self.extractor.extract_features_from_file(str(wav_path))

            for patch in patches:
                patch = self._ensure_hwc(patch)
                window_id = str(uuid.uuid4())
                save_path = self.output_dir / f"{window_id}.npz"
                np.savez(save_path, input=patch)

                rows.append({
                    "window_id": window_id,
                    "filename": wav_path.name,
                    "label": label,
                    "npy_path": str(save_path),
                })

        if rows:
            self._append_csv(rows)

    def upload_single_file(self, file_path: str | Path, label: str) -> None:
        file_path = Path(file_path)
        patches = self.extractor.extract_features_from_file(str(file_path))

        rows = []

        for patch in patches:
            patch = self._ensure_hwc(patch)
            window_id = str(uuid.uuid4())
            save_path = self.output_dir / f"{window_id}.npz"
            np.savez(save_path, input=patch)

            rows.append({
                "window_id": window_id,
                "filename": file_path.name,
                "label": label,
                "npy_path": str(save_path),
            })

        if rows:
            self._append_csv(rows)

    def _append_csv(self, rows: list[dict]) -> None:
        file_exists = self.output_csv.exists()

        with open(self.output_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_COLUMNS)

            if not file_exists:
                writer.writeheader()

            writer.writerows(rows)

    def prepare_dataset_once(
        self,
        disabled_labels: list[str] | None,
        downsampling: bool,
        test_size: float,
        val_from_test: float,
        scaler_sample_limit: int = 4000,
    ) -> None:
        df = self._load_dataset_csv(self.output_csv)

        if disabled_labels:
            df = df[~df["label"].isin(disabled_labels)]
            if df.empty:
                raise ValueError("All labels removed by disabled_labels")

        if downsampling:
            df = self._balanced_downsample(df)

        labels = sorted(df["label"].unique().tolist())
        label_to_idx = {label: i for i, label in enumerate(labels)}

        train_idx, val_idx, test_idx = self._song_wise_split(
            df,
            test_size=test_size,
            val_from_test=val_from_test,
        )

        scaler = self._compute_global_mean_std(
            df.iloc[train_idx]["npy_path"].tolist(),
            sample_limit=scaler_sample_limit,
        )

        dataset_path = Path(CNN_DATASET_PATH)
        dataset_path.mkdir(parents=True, exist_ok=True)

        filtered_csv_path = dataset_path / "filtered_dataset.csv"
        df.to_csv(filtered_csv_path, index=False)

        meta = {
            "labels": labels,
            "label_to_idx": label_to_idx,
            "train_idx": train_idx.tolist(),
            "val_idx": val_idx.tolist(),
            "test_idx": test_idx.tolist(),
            "filtered_csv": str(filtered_csv_path),
        }

        with open(dataset_path / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f)

        joblib.dump(scaler, SCALER_PATH)

    @staticmethod
    def _ensure_hwc(arr: np.ndarray) -> np.ndarray:
        arr = np.asarray(arr, dtype=np.float32)

        if arr.ndim == 3 and arr.shape[0] <= 6:
            arr = np.transpose(arr, (1, 2, 0))
        elif arr.ndim == 2:
            arr = arr[..., np.newaxis]
        elif arr.ndim != 3:
            raise ValueError(f"Unexpected tensor shape: {arr.shape}")

        return arr

    @staticmethod
    def _load_dataset_csv(csv_path: Path) -> pd.DataFrame:
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV not found at {csv_path}")

        df = pd.read_csv(csv_path)

        required = {"window_id", "filename", "label", "npy_path"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"CSV missing columns: {missing}")

        return df

    @staticmethod
    def _balanced_downsample(df: pd.DataFrame) -> pd.DataFrame:
        counts = df["label"].value_counts()
        min_count = counts.min()

        parts = []
        for label in sorted(counts.index):
            part = df[df["label"] == label].sample(
                min_count,
                random_state=42,
            )
            parts.append(part)

        return (
            pd.concat(parts)
            .sample(frac=1.0, random_state=42)
            .reset_index(drop=True)
        )

    @staticmethod
    def _song_wise_split(
        df: pd.DataFrame,
        test_size: float,
        val_from_test: float,
    ):
        df = df.copy()
        df["song_id"] = df["filename"].astype(str).str.split("_part").str[0]

        indices = np.arange(len(df))
        labels = df["label"].values
        groups = df["song_id"].values

        gss = GroupShuffleSplit(
            n_splits=1,
            test_size=test_size,
            random_state=42,
        )
        train_idx, temp_idx = next(gss.split(indices, labels, groups))

        temp_labels = labels[temp_idx]

        sss = StratifiedShuffleSplit(
            n_splits=1,
            test_size=val_from_test,
            random_state=42,
        )
        val_rel, test_rel = next(
            sss.split(temp_idx.reshape(-1, 1), temp_labels)
        )

        val_idx = temp_idx[val_rel]
        test_idx = temp_idx[test_rel]

        return train_idx, val_idx, test_idx

    @staticmethod
    def _compute_global_mean_std(
        npy_paths: list[str],
        sample_limit: int,
    ) -> dict:
        if len(npy_paths) > sample_limit:
            rng = np.random.default_rng(42)
            npy_paths = rng.choice(npy_paths, sample_limit, replace=False)

        s_sum = 0.0
        s_sq_sum = 0.0
        count = 0

        for path in npy_paths:
            arr = np.load(path)["input"].astype(np.float32).ravel()
            s_sum += arr.sum()
            s_sq_sum += np.square(arr).sum()
            count += arr.size

        mean = float(s_sum / count)
        var = float(s_sq_sum / count - mean * mean)
        std = float(np.sqrt(var)) if var > 0 else 1.0

        return {"mean": mean, "std": std}
