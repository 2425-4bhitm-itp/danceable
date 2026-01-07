import json
import os

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from coremltools.converters.mil.testing_reqs import tf
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import griddata
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

from config.paths import SCALER_PATH


class DanceModelEvaluator:
    def __init__(self, model_path, meta_path, output_dir="evaluation_results", disabled_labels=None):
        self.scaler = None
        self.test_idx = None
        self.val_idx = None
        self.dataset_df = None
        self.label_to_idx = None
        self.train_idx = None
        self.model_path = model_path
        self.meta_path = meta_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.model = None
        self.labels = None
        self.disabled_labels = disabled_labels or []

    def load_resources(self):
        self.model = tf.keras.models.load_model(self.model_path)

        with open(self.meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.labels = meta["labels"]
        self.label_to_idx = meta["label_to_idx"]
        self.disabled_labels = self.disabled_labels or []

        filtered_csv_path = meta["filtered_csv"]
        self.dataset_df = pd.read_csv(filtered_csv_path)

        self.train_idx = np.array(meta["train_idx"])
        self.val_idx = np.array(meta["val_idx"])
        self.test_idx = np.array(meta["test_idx"])

        self.scaler = joblib.load(SCALER_PATH)

    def load_preprocessed_data(self):
        df = self.dataset_df

        def load_split(indices):
            subset = df.iloc[indices]
            X_list = []
            y_list = []

            for _, row in subset.iterrows():
                label = row["label"]
                if label in self.disabled_labels:
                    continue

                arr = np.load(row["npy_path"])["input"].astype(np.float32)
                # Apply normalization
                arr = (arr - self.scaler["mean"]) / self.scaler["std"]

                X_list.append(arr)
                y_list.append(self.label_to_idx[label])

            if not X_list:
                raise ValueError("No samples left after applying disabled_labels")

            X = np.stack(X_list, axis=0)
            y = np.array(y_list, dtype=np.int64)
            return X, y

        sets = {
            "train": load_split(self.train_idx),
            "val": load_split(self.val_idx),
            "test": load_split(self.test_idx),
        }

        return sets

    def _plot_confusion_matrix(self, cm_df, set_name):
        base_colors = ["#f3e8f7", "#d2b5e0", "#a06bb8", "#763491"]
        purple_map = LinearSegmentedColormap.from_list("brand_purple", base_colors)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm_df, annot=True, fmt=".1%", cmap=purple_map, cbar=True)
        plt.title("Confusion Matrix")
        plt.ylabel("True")
        plt.xlabel("Predicted")
        out_path = os.path.join(self.output_dir, f"confusion_matrix_{set_name}.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()

    def _plot_3d_landscape(self, cm_df, set_name):
        z = -cm_df.values
        x_labels = cm_df.columns
        y_labels = cm_df.index
        x = np.arange(z.shape[1])
        y = np.arange(z.shape[0])
        X, Y = np.meshgrid(x, y)
        xi = np.linspace(x.min(), x.max(), 200)
        yi = np.linspace(y.min(), y.max(), 200)
        XI, YI = np.meshgrid(xi, yi)
        ZI = griddata((X.ravel(), Y.ravel()), z.ravel(), (XI, YI), method="cubic")
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")
        surf = ax.plot_surface(XI, YI, ZI, cmap="inferno", edgecolor="none", linewidth=0, antialiased=True)
        ax.contourf(XI, YI, ZI, zdir="z", offset=ZI.min(), cmap="inferno", alpha=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45, ha="right")
        ax.set_yticks(y)
        ax.set_yticklabels(y_labels)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_zlabel("Value")
        ax.set_title("Confusion Matrix Landscape Inverted")
        fig.colorbar(surf, shrink=0.5, aspect=10)
        out_path = os.path.join(self.output_dir, f"confusion_matrix_3d_{set_name}.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()

    def _plot_3d_landscape_interactive(self, cm_df, set_name):
        z = cm_df.values.astype(float)
        z_inv = -z
        x_labels = cm_df.columns
        y_labels = cm_df.index
        x = np.arange(z.shape[1])
        y = np.arange(z.shape[0])
        X, Y = np.meshgrid(x, y)
        xi = np.linspace(x.min(), x.max(), 200)
        yi = np.linspace(y.min(), y.max(), 200)
        XI, YI = np.meshgrid(xi, yi)
        ZI_inv = griddata((X.ravel(), Y.ravel()), z_inv.ravel(), (XI, YI), method="cubic")
        nan_mask = np.isnan(ZI_inv)
        if nan_mask.any():
            ZI_lin = griddata((X.ravel(), Y.ravel()), z_inv.ravel(), (XI, YI), method="linear")
            ZI_inv[nan_mask] = ZI_lin[nan_mask]
        fig = go.Figure(data=[go.Surface(x=XI, y=YI, z=ZI_inv, colorscale="Inferno", showscale=True)])
        fig.update_layout(
            title="Interactive Confusion Matrix Landscape Inverted",
            scene=dict(
                xaxis=dict(tickmode="array", tickvals=x, ticktext=list(x_labels), title="Predicted"),
                yaxis=dict(tickmode="array", tickvals=y, ticktext=list(y_labels), title="True"),
                zaxis=dict(title="Value", tickmode="auto", tickformat=".2f")
            ),
            width=1000,
            height=900
        )
        out_path = os.path.join(self.output_dir, f"confusion_matrix_3d_{set_name}.html")
        fig.write_html(out_path, include_plotlyjs="cdn")

    def _plot_class_f1(self, report_df):
        class_rows = report_df.iloc[:-3]
        f1_scores = class_rows["f1-score"]
        plt.figure(figsize=(12, 6))
        sns.barplot(x=f1_scores.index, y=f1_scores.values)
        plt.xticks(rotation=45)
        plt.title("Per Class F1 Score")
        plt.ylabel("F1 Score")
        out_path = os.path.join(self.output_dir, "class_f1_scores.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()

    def _plot_precision_recall(self, report_df):
        class_rows = report_df.iloc[:-3]
        data = pd.DataFrame(
            {"class": class_rows.index, "precision": class_rows["precision"], "recall": class_rows["recall"]}
        )
        data_melted = data.melt(id_vars="class", var_name="metric", value_name="score")
        plt.figure(figsize=(12, 6))
        sns.barplot(x="class", y="score", hue="metric", data=data_melted)
        plt.xticks(rotation=45)
        plt.title("Per Class Precision and Recall")
        out_path = os.path.join(self.output_dir, "precision_recall.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()

    def evaluate_split(self, X, y, set_name, batch_size=128):
        y_pred = []

        for i in range(0, len(X), batch_size):
            batch = X[i:i + batch_size]
            y_prob = self.model.predict(batch, verbose=0)
            y_pred.append(np.argmax(y_prob, axis=1))

        y_pred = np.concatenate(y_pred, axis=0)

        y_true = y

        cm = confusion_matrix(y_true, y_pred, labels=range(len(self.labels)))
        cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
        cm_df = pd.DataFrame(cm_norm, index=self.labels, columns=self.labels)
        cm_df.to_csv(os.path.join(self.output_dir, f"confusion_matrix_{set_name}.csv"))

        report = classification_report(
            y_true, y_pred, target_names=self.labels, output_dict=True, zero_division=0
        )
        report_df = pd.DataFrame(report).transpose()
        report_df.to_csv(os.path.join(self.output_dir, f"class_metrics_{set_name}.csv"))

        self._plot_confusion_matrix(cm_df, set_name)
        self._plot_3d_landscape(cm_df, set_name)
        self._plot_3d_landscape_interactive(cm_df, set_name)
        self._plot_class_f1(report_df)
        self._plot_precision_recall(report_df)

        acc = report.get("accuracy")
        if isinstance(acc, dict):
            acc = acc.get("accuracy")
        return acc

    def evaluate_all(self):
        datasets = self.load_preprocessed_data()
        results = {}
        for split in ["train", "val", "test"]:
            X, y = datasets[split]
            acc = self.evaluate_split(X, y, split)
            results[split] = acc
        return results
