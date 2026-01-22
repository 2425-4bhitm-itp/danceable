import json
import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import tensorflow as tf

from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import griddata
from sklearn.metrics import classification_report, confusion_matrix

from config.paths import SCALER_PATH


class DanceModelEvaluator:
    def __init__(self, model_path, meta_path, output_dir="evaluation_results", disabled_labels=None, apply_scaler=False):
        self.model_path = model_path
        self.meta_path = meta_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.disabled_labels = set(disabled_labels or [])
        self.apply_scaler = apply_scaler

        self.model = None
        self.dataset_df = None
        self.scaler = None

        self.labels = None
        self.label_to_idx = None

        self.train_idx = None
        self.val_idx = None
        self.test_idx = None


    def load_resources(self):
        self.model = tf.keras.models.load_model(self.model_path)

        with open(self.meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.label_to_idx = meta["label_to_idx"]

        self.labels = sorted(self.label_to_idx.keys(), key=lambda k: self.label_to_idx[k])

        filtered_csv_path = meta["filtered_csv"]
        self.dataset_df = pd.read_csv(filtered_csv_path)

        self.train_idx = np.array(meta["train_idx"])
        self.val_idx = np.array(meta["val_idx"])
        self.test_idx = np.array(meta["test_idx"])

        if self.apply_scaler:
            self.scaler = joblib.load(SCALER_PATH)

        print("Loaded model input shape:", self.model.input_shape)
        print("Labels:", self.labels)


    def load_preprocessed_data(self):
        df = self.dataset_df

        def load_split(indices):
            subset = df.iloc[indices]
            X_list, y_list = [], []

            for _, row in subset.iterrows():
                label = row["label"]

                if label in self.disabled_labels:
                    continue

                arr = np.load(row["npy_path"])["input"].astype(np.float32)

                if self.apply_scaler and self.scaler is not None:
                    arr = (arr - self.scaler["mean"]) / self.scaler["std"]

                X_list.append(arr)
                y_list.append(self.label_to_idx[label])

            if not X_list:
                raise RuntimeError("No samples available after filtering labels")

            X = np.stack(X_list, axis=0)
            y = np.array(y_list, dtype=np.int64)

            print("Loaded split:", X.shape, "Unique labels:", np.unique(y))

            return X, y

        result = {
            "train": load_split(self.train_idx),
            "val": load_split(self.val_idx),
            "test": load_split(self.test_idx),
        }


        print(result)

        return result


    def evaluate_split(self, X, y, set_name, batch_size=128):
        assert X.shape[1:] == self.model.input_shape[1:], (
            f"Input shape mismatch: model expects {self.model.input_shape}, got {X.shape}"
        )

        y_pred = []

        for i in range(0, len(X), batch_size):
            batch = X[i:i + batch_size]
            y_prob = self.model.predict(batch, verbose=0)
            y_pred.append(np.argmax(y_prob, axis=1))

        y_pred = np.concatenate(y_pred, axis=0)

        cm = confusion_matrix(y, y_pred, labels=range(len(self.labels)))

        row_sums = cm.sum(axis=1, keepdims=True)
        cm_norm = np.divide(cm, row_sums, where=row_sums != 0)

        cm_df = pd.DataFrame(cm_norm, index=self.labels, columns=self.labels)
        cm_df.to_csv(os.path.join(self.output_dir, f"confusion_matrix_{set_name}.csv"))

        report = classification_report(
            y, y_pred, target_names=self.labels, output_dict=True, zero_division=0
        )

        report_df = pd.DataFrame(report).transpose()
        report_df.to_csv(os.path.join(self.output_dir, f"class_metrics_{set_name}.csv"))

        self._plot_confusion_matrix(cm_df, set_name)
        self._plot_3d_landscape(cm_df, set_name)
        self._plot_3d_landscape_interactive(cm_df, set_name)
        self._plot_class_f1(report_df, set_name)
        self._plot_precision_recall(report_df, set_name)

        return float(report["accuracy"])


    def evaluate_all(self):
        datasets = self.load_preprocessed_data()
        return {split: self.evaluate_split(*datasets[split], split) for split in ["train", "val", "test"]}


    def _plot_confusion_matrix(self, cm_df, set_name):
        base_colors = ["#f3e8f7", "#d2b5e0", "#a06bb8", "#763491"]
        cmap = LinearSegmentedColormap.from_list("brand_purple", base_colors)

        plt.figure(figsize=(10, 8))
        sns.heatmap(cm_df, annot=True, fmt=".1%", cmap=cmap)
        plt.title(f"Confusion Matrix — {set_name}")
        plt.ylabel("True")
        plt.xlabel("Predicted")

        out_path = os.path.join(self.output_dir, f"confusion_matrix_{set_name}.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()


    def _plot_3d_landscape(self, cm_df, set_name):
        z = -cm_df.values
        x = np.arange(z.shape[1])
        y = np.arange(z.shape[0])
        X, Y = np.meshgrid(x, y)

        xi = np.linspace(x.min(), x.max(), 200)
        yi = np.linspace(y.min(), y.max(), 200)
        XI, YI = np.meshgrid(xi, yi)

        ZI = griddata((X.ravel(), Y.ravel()), z.ravel(), (XI, YI), method="cubic")

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")

        surf = ax.plot_surface(XI, YI, ZI, cmap="inferno", edgecolor="none")
        ax.contourf(XI, YI, ZI, zdir="z", offset=ZI.min(), cmap="inferno", alpha=0.7)

        ax.set_title(f"Confusion Landscape — {set_name}")
        fig.colorbar(surf)

        out_path = os.path.join(self.output_dir, f"confusion_matrix_3d_{set_name}.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()


    def _plot_3d_landscape_interactive(self, cm_df, set_name):
        z = -cm_df.values.astype(float)

        x = np.arange(z.shape[1])
        y = np.arange(z.shape[0])
        X, Y = np.meshgrid(x, y)

        xi = np.linspace(x.min(), x.max(), 200)
        yi = np.linspace(y.min(), y.max(), 200)
        XI, YI = np.meshgrid(xi, yi)

        ZI = griddata((X.ravel(), Y.ravel()), z.ravel(), (XI, YI), method="cubic")

        fig = go.Figure(data=[go.Surface(x=XI, y=YI, z=ZI, colorscale="Inferno")])

        fig.update_layout(
            title=f"Interactive Confusion Landscape — {set_name}",
            width=1000,
            height=900
        )

        out_path = os.path.join(self.output_dir, f"confusion_matrix_3d_{set_name}.html")
        fig.write_html(out_path, include_plotlyjs="cdn")


    def _plot_class_f1(self, report_df, set_name):
        class_rows = report_df.iloc[:-3]
        f1 = class_rows["f1-score"]

        plt.figure(figsize=(12, 6))
        sns.barplot(x=f1.index, y=f1.values)
        plt.xticks(rotation=45)
        plt.title(f"F1 Score — {set_name}")

        out_path = os.path.join(self.output_dir, f"class_f1_scores_{set_name}.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()


    def _plot_precision_recall(self, report_df, set_name):
        class_rows = report_df.iloc[:-3]

        data = pd.DataFrame({
            "class": class_rows.index,
            "precision": class_rows["precision"],
            "recall": class_rows["recall"]
        })

        melted = data.melt(id_vars="class", var_name="metric", value_name="score")

        plt.figure(figsize=(12, 6))
        sns.barplot(x="class", y="score", hue="metric", data=melted)
        plt.xticks(rotation=45)
        plt.title(f"Precision vs Recall — {set_name}")

        out_path = os.path.join(self.output_dir, f"precision_recall_{set_name}.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()
