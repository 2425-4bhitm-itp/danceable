import json
import joblib
import numpy as np
import coremltools as ct
from pathlib import Path

from training.model_cnn import (
    build_cnn,
    make_tf_dataset,
    load_prepared_dataset,
)
from config.paths import (
    CNN_OUTPUT_CSV,
    CNN_DATASET_PATH,
    CNN_WEIGHTS_PATH,
    CNN_MODEL_PATH,
    COREML_PATH,
)


def evaluate_and_export():
    print("Evaluator: loading prepared dataset")

    (
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        meta,
        scaler,
    ) = load_prepared_dataset(Path(CNN_OUTPUT_CSV))

    labels = meta["labels"]
    num_classes = len(labels)

    sample = np.load(train_paths[0])["input"].astype(np.float32)
    while sample.ndim > 3:
        sample = sample.squeeze(0)
    if sample.ndim == 2:
        sample = sample[..., np.newaxis]

    input_shape = sample.shape

    test_paths = [meta["test_idx"][i] for i in range(len(meta["test_idx"]))]

    df_test_paths = []
    df_test_labels = []

    import pandas as pd
    df = pd.read_csv(CNN_OUTPUT_CSV)

    for idx in meta["test_idx"]:
        df_test_paths.append(df.iloc[idx]["npy_path"])
        df_test_labels.append(meta["label_to_idx"][df.iloc[idx]["label"]])

    test_ds = make_tf_dataset(
        df_test_paths,
        df_test_labels,
        input_shape,
        num_classes,
        batch_size=64,
        shuffle=False,
    )

    print("Evaluator: building model")
    model = build_cnn(
        input_shape=input_shape,
        num_classes=num_classes,
    )
    model.load_weights(CNN_WEIGHTS_PATH)

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
        "input_shape": input_shape,
    }
