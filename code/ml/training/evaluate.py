import json
import joblib
import numpy as np
import coremltools as ct
from pathlib import Path
from training.model_cnn import (
    make_tf_dataset,
    load_dataset,
    song_wise_split,
    build_cnn
)
from config.paths import (
    CNN_OUTPUT_CSV,
    CNN_LABELS_PATH,
    SCALER_PATH,
    CNN_WEIGHTS_PATH,
    CNN_MODEL_PATH,
    COREML_PATH
)


def evaluate_and_export(weights):
    print("Evaluator: loading artifacts", flush=True)

    df = load_dataset(Path(CNN_OUTPUT_CSV))
    labels = json.load(open(CNN_LABELS_PATH))
    scaler = joblib.load(SCALER_PATH)

    label_to_idx = {l: i for i, l in enumerate(labels)}

    sample_arr = np.load(df.iloc[0]["npy_path"])["input"].astype(np.float32)
    while sample_arr.ndim > 3:
        sample_arr = sample_arr.squeeze(0)
    if sample_arr.ndim == 2:
        sample_arr = sample_arr[..., np.newaxis]

    input_shape = sample_arr.shape
    num_classes = len(labels)

    _, _, test_idx = song_wise_split(df, test_size=0.2, val_from_test=0.5)

    test_ds = make_tf_dataset(
        test_idx,
        df,
        scaler,
        label_to_idx,
        input_shape,
        num_classes,
        batch_size=64,
        shuffle=False
    )

    print("Evaluator: building model", flush=True)
    model = build_cnn(input_shape, num_classes)
    model.set_weights(weights)
    model.save_weights(CNN_WEIGHTS_PATH)

    print("Evaluator: running evaluation", flush=True)
    loss, acc = model.evaluate(test_ds, verbose=1)

    print(f"Evaluator: loss={loss:.4f}, acc={acc:.4f}", flush=True)

    print("Evaluator: saving SavedModel", flush=True)
    model.save(CNN_MODEL_PATH)

    print("Evaluator: converting to CoreML", flush=True)
    cm = ct.convert(
        model,
        source="tensorflow",
        inputs=[ct.TensorType(shape=(1,) + input_shape)]
    )
    cm.save(COREML_PATH)

    metrics = {
        "loss": float(loss),
        "accuracy": float(acc),
        "labels": labels,
        "input_shape": input_shape
    }

    print(f"Evaluator: completed successfully {metrics}", flush=True)
    return metrics
