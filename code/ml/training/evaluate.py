import json
import joblib
import numpy as np
import coremltools as ct
from pathlib import Path

import pandas as pd
from sympy.parsing.sympy_parser import null

from training.model_cnn import (
    build_cnn,
    make_tf_dataset,
    load_prepared_dataset,
)
from config.paths import (
    CNN_WEIGHTS_PATH,
    CNN_MODEL_PATH,
    COREML_PATH,
)


def evaluate_and_export(model_config = null, checkpoint_dir: Path = CNN_WEIGHTS_PATH):
    print("Evaluator: loading prepared dataset")

    (
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        meta,
        scaler,
    ) = load_prepared_dataset()

    labels = meta["labels"]
    num_classes = len(labels)

    sample = np.load(train_paths[0])["input"].astype(np.float32)
    while sample.ndim > 3:
        sample = sample.squeeze(0)
    if sample.ndim == 2:
        sample = sample[..., np.newaxis]

    input_shape = sample.shape

    df = pd.read_csv(meta["filtered_csv"])

    test_paths = df.iloc[meta["test_idx"]]["npy_path"].astype(str).tolist()
    test_labels = [
        meta["label_to_idx"][df.iloc[i]["label"]]
        for i in meta["test_idx"]
    ]

    test_ds = make_tf_dataset(
        test_paths,
        test_labels,
        input_shape,
        num_classes,
        batch_size=64,
        shuffle=False,
    )

    print("Evaluator: building model")
    model = build_cnn(
        input_shape=input_shape,
        num_classes=num_classes,
        **(model_config or {}),
    )

    model.load_weights(checkpoint_dir)

    print("Evaluator: evaluating")
    loss, acc = model.evaluate(test_ds, verbose=1)

    print(f"Evaluator: loss={loss:.4f}, acc={acc:.4f}")

    print("Evaluator: saving SavedModel")
    model.save(CNN_MODEL_PATH)

    print("Evaluator: exporting CoreML")
    mlmodel = ct.convert(
        model,
        source="tensorflow",
        inputs=[ct.TensorType(shape=(1,) + input_shape)],
    )
    mlmodel.save(COREML_PATH)

    return {
        "loss": float(loss),
        "accuracy": float(acc),
        "labels": labels,
        "input_shape": input_shape
    }
