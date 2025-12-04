import json
import os
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import griddata
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from tensorflow.keras.models import load_model
import plotly.graph_objects as go

from config.paths import BASE_MODEL_DIR


class DanceModelEvaluator:
    def __init__(self,
                 model_path,
                 labels_path,
                 output_dir="evaluation_results"):

        self.model_path = model_path
        self.labels_path = labels_path
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

        self.model = None
        self.labels = None

    def load_resources(self):
        """Loads the CNN model and label ordering"""
        print("Loading model and labels")
        self.model = load_model(self.model_path)

        with open(self.labels_path, "r") as f:
            self.labels = json.load(f)

        print(f"Loaded model and {len(self.labels)} labels")


    def evaluate(self):
        """
        Produces confusion matrix and classification metrics.
        Saves everything to CSV files.
        """
        print("Running model predictions")

        y_prob = self.model.predict(self.X, verbose=0)
        y_pred = np.argmax(y_prob, axis=1)

        label_to_index = {label: i for i, label in enumerate(self.labels)}
        y_true = np.array([label_to_index[label] for label in self.y])

        print("Building confusion matrix")

        cm = confusion_matrix(y_true, y_pred)
        cm_df = pd.DataFrame(cm, index=self.labels, columns=self.labels)
        cm_csv = os.path.join(self.output_dir, "confusion_matrix.csv")
        cm_df.to_csv(cm_csv)
        print(f"Confusion matrix saved to {cm_csv}")

        print("Building classification report")

        report = classification_report(
            y_true,
            y_pred,
            target_names=self.labels,
            output_dict=True
        )

        report_df = pd.DataFrame(report).transpose()
        report_csv = os.path.join(self.output_dir, "class_metrics.csv")
        report_df.to_csv(report_csv)
        print(f"Class metrics saved to {report_csv}")

        self._plot_confusion_matrix(cm_df, False)
        self._plot_class_f1(report_df)
        self._plot_precision_recall(report_df)

        print("Evaluation completed")


    def _plot_confusion_matrix(self, cm_df, is_test_set, set_name=""):
        base_colors = ["#f3e8f7", "#d2b5e0", "#a06bb8", "#763491"]
        purple_map = LinearSegmentedColormap.from_list("brand_purple", base_colors)

        plt.figure(figsize=(10, 8))

        sns.heatmap(
            cm_df,
            annot=True,
            fmt=".1%",
            cmap=purple_map,
            cbar=True
        )
        plt.title("Confusion Matrix")
        plt.ylabel("True")
        plt.xlabel("Predicted")

        if is_test_set:
            out_path = os.path.join(self.output_dir, f"confusion_matrix_{set_name}.png")
        else:
            out_path = os.path.join(self.output_dir, "confusion_matrix.png")

        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()

    def _plot_3d_landscape(self, cm_df, is_test_set, set_name=""):
        z = cm_df.values
        z = -z

        x_labels = cm_df.columns
        y_labels = cm_df.index

        x = np.arange(z.shape[1])
        y = np.arange(z.shape[0])
        X, Y = np.meshgrid(x, y)

        xi = np.linspace(x.min(), x.max(), 200)
        yi = np.linspace(y.min(), y.max(), 200)
        XI, YI = np.meshgrid(xi, yi)
        ZI = griddata((X.ravel(), Y.ravel()), z.ravel(), (XI, YI), method='cubic')

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")

        surf = ax.plot_surface(
            XI,
            YI,
            ZI,
            cmap='inferno',
            edgecolor='none',
            linewidth=0,
            antialiased=True
        )

        ax.contourf(XI, YI, ZI, zdir='z', offset=ZI.min(), cmap='inferno', alpha=0.7)

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45, ha="right")
        ax.set_yticks(y)
        ax.set_yticklabels(y_labels)

        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_zlabel("Value")
        ax.set_title("Confusion Matrix Landscape (Inverted)")

        z_ticks = np.linspace(ZI.min(), ZI.max(), 5)
        ax.set_zticks(z_ticks)
        ax.set_zticklabels([f"{-t:.2f}" for t in z_ticks])

        fig.colorbar(surf, shrink=0.5, aspect=10)

        if is_test_set:
            out_path = os.path.join(self.output_dir, f"confusion_matrix_3d_{set_name}.png")
        else:
            out_path = os.path.join(self.output_dir, "confusion_matrix_3d.png")

        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()

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

        data = pd.DataFrame({
            "class": class_rows.index,
            "precision": class_rows["precision"],
            "recall": class_rows["recall"]
        })

        data_melted = data.melt(id_vars="class", var_name="metric", value_name="score")

        plt.figure(figsize=(12, 6))
        sns.barplot(x="class", y="score", hue="metric", data=data_melted)
        plt.xticks(rotation=45)
        plt.title("Per Class Precision and Recall")

        out_path = os.path.join(self.output_dir, "precision_recall.png")
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()

    def _plot_3d_landscape_interactive(self, cm_df, is_test_set, set_name=""):
        # original data
        z = cm_df.values.astype(float)

        # invert for gravitational well effect
        z_inv = -z

        x_labels = cm_df.columns
        y_labels = cm_df.index

        x = np.arange(z.shape[1])
        y = np.arange(z.shape[0])
        X, Y = np.meshgrid(x, y)

        # Smooth interpolation on the inverted values
        xi = np.linspace(x.min(), x.max(), 200)
        yi = np.linspace(y.min(), y.max(), 200)
        XI, YI = np.meshgrid(xi, yi)

        # cubic interpolation will only be valid INSIDE convex hull
        ZI_inv = griddata(
            (X.ravel(), Y.ravel()),
            z_inv.ravel(),
            (XI, YI),
            method="cubic"
        )

        # Any invalid corner values become NaN. Replace with linear interpolation.
        nan_mask = np.isnan(ZI_inv)
        if nan_mask.any():
            ZI_inv_linear = griddata(
                (X.ravel(), Y.ravel()),
                z_inv.ravel(),
                (XI, YI),
                method="linear"
            )
            ZI_inv[nan_mask] = ZI_inv_linear[nan_mask]

        fig = go.Figure(data=[
            go.Surface(
                x=XI,
                y=YI,
                z=ZI_inv,
                colorscale="Inferno",
                showscale=True
            )
        ])

        # Correct axis labels showing original positive values
        fig.update_layout(
            title="Interactive Confusion Matrix Landscape (Inverted)",
            scene=dict(
                xaxis=dict(
                    tickmode="array",
                    tickvals=x,
                    ticktext=list(x_labels),
                    title="Predicted"
                ),
                yaxis=dict(
                    tickmode="array",
                    tickvals=y,
                    ticktext=list(y_labels),
                    title="True"
                ),
                zaxis=dict(
                    title="Value",
                    tickmode="auto",
                    tickformat=".2f"
                )
            ),
            width=1000,
            height=900
        )

        if is_test_set:
            out_path = os.path.join(self.output_dir, f"confusion_matrix_3d_{set_name}.html")
        else:
            out_path = os.path.join(self.output_dir, "confusion_matrix_3d.html")

        fig.write_html(out_path, include_plotlyjs="cdn")

    def evaluate_from_arrays(self, X, y, set_name=""):
        """
        Evaluate the model using already-prepared arrays (X_test, y_test).
        No CSV loading, no filtering, no scaling.
        This is the preferred method for evaluating a training run correctly.
        """

        print("Running model predictions")

        y_prob = self.model.predict(X, verbose=0)
        y_pred = np.argmax(y_prob, axis=1)

        # Determine what format y is in
        if isinstance(y[0], str):
            # String labels
            label_to_index = {label: i for i, label in enumerate(self.labels)}
            y_true = np.array([label_to_index[label] for label in y])
        elif y.ndim == 2 and y.shape[1] > 1:
            # One-hot labels
            y_true = np.argmax(y, axis=1)
        else:
            # Already integer labels
            y_true = y.reshape(-1)

        print("Building confusion matrix")

        cm = confusion_matrix(y_true, y_pred)
        cm_normalized = cm / cm.sum(axis=1, keepdims=True)
        cm_df = pd.DataFrame(cm_normalized, index=self.labels, columns=self.labels)
        cm_csv = os.path.join(self.output_dir, "confusion_matrix.csv")
        cm_df.to_csv(cm_csv)

        print(f"Confusion matrix saved to {cm_csv}")

        print("Building classification report")

        report = classification_report(
            y_true,
            y_pred,
            target_names=self.labels,
            output_dict=True,
            zero_division=0
        )

        report_df = pd.DataFrame(report).transpose()
        report_csv = os.path.join(self.output_dir, f"class_metrics_{set_name}.csv")
        report_df.to_csv(report_csv)
        print(f"Class metrics saved to {report_csv}")

        self._plot_confusion_matrix(cm_df, True, set_name)
        self._plot_3d_landscape(cm_df, True, set_name)
        self._plot_3d_landscape_interactive(cm_df, True, set_name)
        self._plot_class_f1(report_df)
        self._plot_precision_recall(report_df)

        print("Evaluation completed using test arrays")

    def evaluate_from_arrays_cnn(self, X, y, set_name=""):
        """
        Evaluate the CNN model using prepared arrays (X, y).
        Works directly with .npy/tensor inputs.
        """

        print(f"Running predictions on {set_name} set")
        y_prob = self.model.predict(X, verbose=0)
        y_pred = np.argmax(y_prob, axis=1)

        # Convert y to integer indices
        if isinstance(y[0], str):
            label_to_index = {label: i for i, label in enumerate(self.labels)}
            y_true = np.array([label_to_index[label] for label in y])
        elif y.ndim == 2 and y.shape[1] > 1:
            y_true = np.argmax(y, axis=1)
        else:
            y_true = y.reshape(-1)

        # Confusion matrix
        from sklearn.metrics import confusion_matrix, classification_report
        import os
        import pandas as pd

        cm = confusion_matrix(y_true, y_pred)
        cm_normalized = cm / cm.sum(axis=1, keepdims=True)
        cm_df = pd.DataFrame(cm_normalized, index=self.labels, columns=self.labels)
        cm_csv = os.path.join(self.output_dir, f"confusion_matrix_{set_name}.csv")
        cm_df.to_csv(cm_csv)
        print(f"Confusion matrix saved to {cm_csv}")

        # Classification report
        report = classification_report(y_true, y_pred, target_names=self.labels, output_dict=True, zero_division=0)
        report_df = pd.DataFrame(report).transpose()
        report_csv = os.path.join(self.output_dir, f"class_metrics_{set_name}.csv")
        report_df.to_csv(report_csv)
        print(f"Class metrics saved to {report_csv}")

        # Optional: plotting (keep if you have plotting methods)
        self._plot_confusion_matrix(cm_df, True, set_name)
        self._plot_3d_landscape(cm_df, True, set_name)
        self._plot_3d_landscape_interactive(cm_df, True, set_name)
        self._plot_class_f1(report_df)
        self._plot_precision_recall(report_df)

        print(f"Evaluation completed for {set_name} set")

    def load_preprocessed_data(self):
        data_dir = Path(BASE_MODEL_DIR)
        datasets = {}
        for split in ["train", "val", "test"]:
            path = data_dir / f"{split}_data.npz"
            if not path.exists():
                raise FileNotFoundError(f"{split}_data.npz not found, run training first")
            arr = np.load(path, allow_pickle=True)
            datasets[split] = (arr["X"], arr["y"])
        return datasets