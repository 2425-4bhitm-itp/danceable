import gc
import json
import os
import time
from pathlib import Path
from datetime import datetime

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf

from config.paths import HYPER_ENV_PATH, BASE_MODEL_DIR, RESULTS_DIR
from training.evaluate import evaluate_and_export
from training.model_cnn import train_model

POD_NAME = os.environ["POD_NAME"]
POD_INDEX = int(os.environ["POD_INDEX"])

print(f"Hyper worker started: pod={POD_NAME}, index={POD_INDEX}")


def wait_for_run():
    base = Path(HYPER_ENV_PATH)
    while True:
        runs = sorted(base.glob("run_*"))
        if runs:
            return runs[-1]
        time.sleep(1)


def run_hyper(run_dir: Path):
    run_id = run_dir.name
    runs_file = run_dir / f"runs_{POD_INDEX}.json"

    if not runs_file.exists():
        print(f"No shard for pod {POD_INDEX}")
        return

    runs = json.load(open(runs_file))

    out_dir = RESULTS_DIR / "jsons"
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx, cfg in enumerate(runs):
        train_cfg = cfg["train"]
        model_cfg = cfg["model"]

        tag = f"{run_id}_{POD_INDEX}_{idx}"
        checkpoint_path = RESULTS_DIR / f"checkpoints/{tag}.h5"

        print(f"Running {tag}")

        start = time.time()

        model = train_model(
            batch_size=train_cfg.get("batch_size", 128),
            epochs=train_cfg.get("epochs", 100),
            model_config=model_cfg,
            verbose=0,
            checkpoint_dir=checkpoint_path,
        )

        elapsed = time.time() - start

        loss, accuracy, labels, input_shape = evaluate_and_export(
            model_cfg,
            checkpoint_path,
        )

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "pod": POD_INDEX,
            "index": idx,
            "train_config": train_cfg,
            "model_config": model_cfg,
            "elapsed_seconds": elapsed,
            "loss": loss,
            "accuracy": accuracy,
            "labels": labels,
            "input_shape": input_shape,
        }

        with open(out_dir / f"result_{tag}.json", "w") as f:
            json.dump(result, f, indent=2)

        tf.keras.backend.clear_session()
        gc.collect()


if __name__ == "__main__":
    run_dir = wait_for_run()
    print(f"Found run directory: {run_dir}")
    run_hyper(run_dir)
