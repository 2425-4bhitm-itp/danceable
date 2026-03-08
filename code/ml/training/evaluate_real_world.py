"""
Real-world evaluation on phone-recorded audio.

Folder layout expected:
    /app/song-storage/songs/test/<label>/<audio_file>.(wav|mp3|webm|caf)

Each subfolder name is treated as the ground-truth label.
The model predicts a label for every file (averaged over its patches),
and we compare predictions against ground truth.
"""

import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import classification_report, confusion_matrix

from config.paths import (
    CNN_MODEL_PATH,
    CNN_LABELS_PATH,
    SCALER_PATH,
    EVALUATION_RESULTS_DIR,
)

# Lazy imports to avoid circular dependency with app.py
_tf = None


def _get_tf():
    global _tf
    if _tf is None:
        import tensorflow as tf
        _tf = tf
    return _tf


# ---------------------------------------------------------------------------
# Supported audio extensions (same as the rest of the project)
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".webm", ".caf"}


def _convert_to_wav_if_needed(file_path: str, converter) -> str:
    """Re-use the converter helpers that already exist in app.py."""
    if file_path.endswith(".wav"):
        return file_path
    if file_path.endswith(".webm"):
        return converter.convert_webm_to_wav(file_path, file_path.replace(".webm", ".wav"))
    if file_path.endswith(".caf"):
        return converter.convert_caf_to_wav(file_path, file_path.replace(".caf", ".wav"))
    if file_path.endswith(".mp3"):
        return converter.convert_mp3_to_wav(file_path, file_path.replace(".mp3", ".wav"))
    return file_path


# ---------------------------------------------------------------------------
# Core evaluator
# ---------------------------------------------------------------------------

class RealWorldEvaluator:
    """
    Evaluates the CNN model against a labelled folder of phone-recorded audio.

    Parameters
    ----------
    test_root : str | Path
        Root directory whose immediate subdirectories are label names.
    extractor : AudioFeatureExtractorCNN
        Feature extractor shared with the rest of the app.
    file_converter : module, optional
        The `file_converter` utility module (passed in to avoid circular imports).
    output_dir : str | Path, optional
        Where to save plots / CSVs.  Defaults to EVALUATION_RESULTS_DIR.
    apply_scaler : bool
        Whether to normalise patches with the saved scaler before inference.
    """

    def __init__(
        self,
        test_root,
        extractor,
        file_converter=None,
        output_dir=None,
        apply_scaler: bool = True,
        temperature: float = 1.0,
    ):
        self.temperature: float = temperature,
        self.test_root = Path(test_root)
        self.extractor = extractor
        self.file_converter = file_converter
        self.output_dir = Path(output_dir or EVALUATION_RESULTS_DIR) / "real_world"
        self.apply_scaler = apply_scaler

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._model = None
        self._labels = None
        self._scaler = None

    # ------------------------------------------------------------------
    # Resource loading
    # ------------------------------------------------------------------

    def _load_resources(self):
        tf = _get_tf()

        if self._model is None:
            self._model = tf.keras.models.load_model(CNN_MODEL_PATH)

        if self._labels is None:
            with open(CNN_LABELS_PATH) as f:
                self._labels = json.load(f)

        if self._scaler is None and self.apply_scaler:
            self._scaler = joblib.load(SCALER_PATH)

    # ------------------------------------------------------------------
    # Inference for a single file
    # ------------------------------------------------------------------

    def _predict_file(self, file_path: str) -> str | None:
        """Return the predicted label for one audio file (majority vote over patches)."""
        if self.file_converter:
            wav_path = _convert_to_wav_if_needed(file_path, self.file_converter)
        else:
            wav_path = file_path

        try:
            patches = self.extractor.extract_features_from_file(wav_path)
        except Exception as e:
            print(f"  [WARN] Feature extraction failed for {file_path}: {e}")
            return None

        if not patches:
            print(f"  [WARN] No patches extracted from {file_path}")
            return None

        batch = np.asarray(patches, dtype=np.float32)

        # Squeeze any extra leading dim (some extractors add batch dim)
        if batch.ndim == 5 and batch.shape[1] == 1:
            batch = batch[:, 0]

        if self.apply_scaler and self._scaler is not None:
            mean = batch.mean(axis=(1, 2, 3), keepdims=True)
            std = batch.std(axis=(1, 2, 3), keepdims=True)
            batch = (batch - mean) / (std + 1e-8)

        probs = self._model.predict(batch, verbose=0)

        # Temperature scaling — flatten overconfident predictions
        if self.temperature != 1.0:
            log_probs = np.log(probs + 1e-8) / self.temperature
            probs = np.exp(log_probs - log_probs.max(axis=-1, keepdims=True))
            probs = probs / probs.sum(axis=-1, keepdims=True)

        avg_probs = probs.mean(axis=0)
        pred_idx = int(np.argmax(avg_probs))

        return self._labels[pred_idx]

    # ------------------------------------------------------------------
    # Full evaluation
    # ------------------------------------------------------------------

    def evaluate(self) -> dict:
        """
        Walk test_root, predict every audio file, and compute metrics.

        Returns
        -------
        dict with keys: accuracy, per_class_report, summary_path
        """
        self._load_resources()

        label_dirs = sorted(
            [d for d in self.test_root.iterdir() if d.is_dir()]
        )

        if not label_dirs:
            raise FileNotFoundError(
                f"No label subdirectories found under {self.test_root}"
            )

        known_labels = set(self._labels)
        y_true, y_pred, file_names = [], [], []
        skipped = 0
        errors = 0

        for label_dir in label_dirs:
            true_label = label_dir.name

            if true_label not in known_labels:
                print(f"[WARN] Folder '{true_label}' not in model labels — skipping.")
                skipped += 1
                continue

            audio_files = [
                f for f in label_dir.iterdir()
                if f.suffix.lower() in SUPPORTED_EXTENSIONS
            ]

            if not audio_files:
                print(f"[INFO] No audio files in {label_dir} — skipping.")
                continue

            print(f"Processing '{true_label}': {len(audio_files)} file(s)")

            for audio_file in sorted(audio_files):
                pred_label = self._predict_file(str(audio_file))

                if pred_label is None:
                    errors += 1
                    continue

                y_true.append(true_label)
                y_pred.append(pred_label)
                file_names.append(audio_file.name)

        if not y_true:
            raise RuntimeError("No files could be evaluated.")

        # ------------------------------------------------------------------
        # Metrics
        # ------------------------------------------------------------------
        present_labels = sorted(set(y_true) | set(y_pred))

        report = classification_report(
            y_true, y_pred,
            labels=present_labels,
            output_dict=True,
            zero_division=0,
        )

        accuracy = float(report["accuracy"])
        cm = confusion_matrix(y_true, y_pred, labels=present_labels)
        row_sums = cm.sum(axis=1, keepdims=True)
        cm_norm = np.divide(cm, row_sums, where=row_sums != 0).astype(float)
        cm_df = pd.DataFrame(cm_norm, index=present_labels, columns=present_labels)

        # ------------------------------------------------------------------
        # Save artefacts
        # ------------------------------------------------------------------
        cm_df.to_csv(self.output_dir / "confusion_matrix_real_world.csv")

        report_df = pd.DataFrame(report).transpose()
        report_df.to_csv(self.output_dir / "class_metrics_real_world.csv")

        per_file_df = pd.DataFrame({
            "filename": file_names,
            "true_label": y_true,
            "predicted_label": y_pred,
            "correct": [t == p for t, p in zip(y_true, y_pred)],
        })
        per_file_df.to_csv(self.output_dir / "per_file_results_real_world.csv", index=False)

        self._plot_confusion_matrix(cm_df)
        self._plot_class_f1(report_df)
        self._plot_precision_recall(report_df)

        summary = {
            "accuracy": round(accuracy, 4),
            "total_files": len(y_true),
            "skipped_unknown_labels": skipped,
            "extraction_errors": errors,
            "per_class": {
                label: {
                    "precision": round(report[label]["precision"], 4),
                    "recall":    round(report[label]["recall"],    4),
                    "f1":        round(report[label]["f1-score"],  4),
                    "support":   int(report[label]["support"]),
                }
                for label in present_labels
                if label in report
            },
            "output_dir": str(self.output_dir),
        }

        with open(self.output_dir / "summary_real_world.json", "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\nReal-world evaluation complete — accuracy: {accuracy:.2%}")
        return summary

    # ------------------------------------------------------------------
    # Plotting helpers  (same brand palette as DanceModelEvaluator)
    # ------------------------------------------------------------------

    def _plot_confusion_matrix(self, cm_df: pd.DataFrame):
        base_colors = ["#f3e8f7", "#d2b5e0", "#a06bb8", "#763491"]
        cmap = LinearSegmentedColormap.from_list("brand_purple", base_colors)

        plt.figure(figsize=(max(8, len(cm_df) + 2), max(6, len(cm_df))))
        sns.heatmap(cm_df, annot=True, fmt=".1%", cmap=cmap)
        plt.title("Confusion Matrix — Real World")
        plt.ylabel("True")
        plt.xlabel("Predicted")
        plt.tight_layout()
        plt.savefig(self.output_dir / "confusion_matrix_real_world.png", dpi=200, bbox_inches="tight")
        plt.close()

    def _plot_class_f1(self, report_df: pd.DataFrame):
        class_rows = report_df.iloc[:-3]  # drop accuracy / macro / weighted rows
        f1 = class_rows["f1-score"]

        plt.figure(figsize=(max(10, len(f1) + 2), 6))
        sns.barplot(x=f1.index, y=f1.values)
        plt.xticks(rotation=45, ha="right")
        plt.title("F1 Score — Real World")
        plt.tight_layout()
        plt.savefig(self.output_dir / "class_f1_scores_real_world.png", dpi=200, bbox_inches="tight")
        plt.close()

    def _plot_precision_recall(self, report_df: pd.DataFrame):
        class_rows = report_df.iloc[:-3]
        data = pd.DataFrame({
            "class":     class_rows.index,
            "precision": class_rows["precision"],
            "recall":    class_rows["recall"],
        })
        melted = data.melt(id_vars="class", var_name="metric", value_name="score")

        plt.figure(figsize=(max(10, len(class_rows) + 2), 6))
        sns.barplot(x="class", y="score", hue="metric", data=melted)
        plt.xticks(rotation=45, ha="right")
        plt.title("Precision vs Recall — Real World")
        plt.tight_layout()
        plt.savefig(self.output_dir / "precision_recall_real_world.png", dpi=200, bbox_inches="tight")
        plt.close()
