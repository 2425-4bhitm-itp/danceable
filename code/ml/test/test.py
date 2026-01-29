import gc
import json
import os
import shutil
import time
from datetime import datetime

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf

from config.paths import HYPER_ENV_PATH, RESULTS_DIR
from training.evaluate import evaluate_and_export
from training.model_cnn import train_model
from pathlib import Path

POD_NAME = os.environ["POD_NAME"]
POD_INDEX = int(os.environ["POD_INDEX"])
is_cleared = False

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
    print(f"{runs_file} for pod {POD_INDEX} in run {run_id}")

    timeout = time.time() + 30
    while not runs_file.exists():
        if time.time() > timeout:
            print(f"Shard still missing after timeout: {runs_file}")
            return
        time.sleep(0.5)

    runs = json.load(open(runs_file))

    out_dir = RESULTS_DIR / "jsons"
    out_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_dir = RESULTS_DIR / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    verbose = 1 if POD_INDEX == 0 else 0

    for idx, cfg in enumerate(runs):
        train_cfg = cfg["train"]
        model_cfg = cfg["model"]

        tag = f"{run_id}_{POD_INDEX}_{idx}"
        checkpoint_path = checkpoint_dir / f"{tag}.h5"

        print(f"Running {tag}")

        start = time.time()

        model = train_model(
            batch_size=train_cfg.get("batch_size", 128),
            epochs=train_cfg.get("epochs", 100),
            model_config=model_cfg,
            verbose=verbose,
            checkpoint_dir=checkpoint_path,
        )

        elapsed = time.time() - start

        results = evaluate_and_export(
            model_cfg,
            checkpoint_path,
        )

        loss = results["loss"]
        accuracy = results["accuracy"]
        labels = results["labels"]
        input_shape = results["input_shape"]

        train_result = {
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

        print(train_result)

        with open(out_dir / f"result_{tag}.json", "w") as f:
            json.dump(train_result, f, indent=2)

        tf.keras.backend.clear_session()
        gc.collect()


if __name__ == "__main__":
    run_dir = wait_for_run()
    print(f"Found run directory: {run_dir}")
    run_hyper(run_dir)
