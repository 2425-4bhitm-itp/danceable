import os
import json
import joblib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from tensorflow.keras.models import load_model


class DanceModelEvaluator:
    """
    Evaluation pipeline for a trained dance classification model.
    Ensures strict feature alignment between training and evaluation
    to avoid dimension mismatches with StandardScaler.
    """

    def __init__(self,
                 model_path,
                 scaler_path,
                 labels_path,
                 features_csv,
                 output_dir="evaluation_results"):

        self.model_path = model_path
        self.scaler_path = scaler_path
        self.labels_path = labels_path
        self.features_csv = features_csv
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

        self.model = None
        self.scaler = None
        self.scaler_features = None
        self.labels = None
        self.df = None
        self.X = None
        self.y = None

    def load_resources(self):
        """
        Loads model, scaler and label ordering.
        Scaler must contain both the fitted scaler and the feature list.
        """
        print("Loading model and scaler")

        self.model = load_model(self.model_path)

        data = joblib.load(self.scaler_path)
        if isinstance(data, dict) and "scaler" in data and "features" in data:
            self.scaler = data["scaler"]
            self.scaler_features = data["features"]
        else:
            raise RuntimeError("Scaler file must contain {'scaler': ..., 'features': [...]}.")

        with open(self.labels_path, "r") as f:
            self.labels = json.load(f)

        print("Resources loaded successfully")

    def load_data(self):
        """
        Loads the feature CSV, extracts X and y,
        verifies feature alignment with the scaler,
        and applies scaling. Removes unknown labels.
        """
        print("Loading feature data")

        self.df = pd.read_csv(self.features_csv)

        # Remove non-feature columns
        original_features = [c for c in self.df.columns if c not in ["filename", "label"]]

        # Check feature consistency
        missing = [f for f in self.scaler_features if f not in original_features]
        extra = [f for f in original_features if f not in self.scaler_features]

        if missing:
            raise ValueError(f"The CSV is missing required features: {missing}")

        if extra:
            print(f"Warning: CSV contains extra features that will be ignored: {extra}")

        # Keep only features the scaler expects
        self.X = self.df[self.scaler_features].values
        self.y = self.df["label"].values

        # Remove rows with labels the model was not trained on
        label_to_index = {label: i for i, label in enumerate(self.labels)}
        valid_mask = np.array([label in label_to_index for label in self.y])

        if not valid_mask.all():
            unknown_labels = sorted(set(self.y[~valid_mask]))
            print(f"Warning: ignoring {len(unknown_labels)} unknown label(s) not in model: {unknown_labels}")

        self.X = self.X[valid_mask]
        self.y = self.y[valid_mask]

        # Scale
        self.X = self.scaler.transform(self.X)

        print(f"Data loaded and scaled successfully ({len(self.y)} samples after filtering unknown labels)")

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
        # Define a custom purple colormap
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
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib import cm

        z = cm_df.values
        x_labels = cm_df.columns
        y_labels = cm_df.index

        # Create grid
        x = np.arange(z.shape[1])
        y = np.arange(z.shape[0])
        X, Y = np.meshgrid(x, y)

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")

        surf = ax.plot_surface(
            X,
            Y,
            z,
            cmap=cm.viridis,
            edgecolor="k",
            linewidth=0.5,
            antialiased=True
        )

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45, ha="right")

        ax.set_yticks(y)
        ax.set_yticklabels(y_labels)

        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_zlabel("Value")

        ax.set_title("Confusion Matrix Landscape")
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
        self._plot_class_f1(report_df)
        self._plot_precision_recall(report_df)

        print("Evaluation completed using test arrays")