import os
import time
import json
import itertools
from pathlib import Path
from datetime import datetime

import tensorflow as tf

from training.model_cnn import train_model
from config.paths import HYPER_ENV_PATH

POD_NAME = os.environ["POD_NAME"]

run_id_file = os.path.join(HYPER_ENV_PATH, "RUN_ID")
state_file = os.path.join(HYPER_ENV_PATH, "STATE")
ready_file = os.path.join(HYPER_ENV_PATH, "READY_WORKERS")

last_seen = -1


def is_chief():
    return POD_NAME.endswith("-0")


def register_ready():
    os.makedirs(HYPER_ENV_PATH, exist_ok=True)
    while True:
        try:
            workers = set()
            if os.path.exists(ready_file):
                with open(ready_file) as f:
                    workers = {l.strip() for l in f if l.strip()}

            if POD_NAME not in workers:
                workers.add(POD_NAME)
                with open(ready_file, "w") as f:
                    for w in sorted(workers):
                        f.write(w + "\n")
            return
        except Exception:
            time.sleep(1)


register_ready()
print(f"{POD_NAME} hyper worker ready")

while True:
    if not os.path.exists(run_id_file):
        time.sleep(1)
        continue

    current = int(open(run_id_file).read().strip())
    if current <= last_seen:
        time.sleep(1)
        continue

    last_seen = current
    print(f"{POD_NAME} starting hyper run {current}")

    search_space = json.load(open(os.path.join(HYPER_ENV_PATH, "SEARCH_SPACE")))

    train_space = search_space.get("train", {})
    model_space = search_space.get("model", {})

    train_keys = list(train_space.keys())
    model_keys = list(model_space.keys())

    train_runs = list(itertools.product(*train_space.values())) or [()]
    model_runs = list(itertools.product(*model_space.values())) or [()]

    strategy = tf.distribute.MultiWorkerMirroredStrategy()

    results = []
    out_dir = Path("/opt/model/hyper_runs")
    if is_chief():
        out_dir.mkdir(parents=True, exist_ok=True)

    for train_vals in train_runs:
        train_cfg = dict(zip(train_keys, train_vals))

        for model_vals in model_runs:
            model_cfg = dict(zip(model_keys, model_vals))

            run_tag = f"{current}_{hash(tuple(train_vals) + tuple(model_vals)) & 0xffff:x}"

            with strategy.scope():
                metrics = train_model(
                    batch_size=train_cfg.get("batch_size", 128),
                    epochs=train_cfg.get("epochs", 100),
                    test_size=train_cfg.get("test_size", 0.2),
                    downsampling=train_cfg.get("downsampling", True),
                    disabled_labels=train_cfg.get("disabled_labels"),
                    model_config=model_cfg
                )

            if is_chief():
                results.append({
                    "run": run_tag,
                    "timestamp": datetime.utcnow().isoformat(),
                    "train": train_cfg,
                    "model": model_cfg,
                    "loss": metrics["loss"],
                    "accuracy": metrics["accuracy"]
                })

    if is_chief():
        json.dump(
            results,
            open(out_dir / f"summary_{current}.json", "w"),
            indent=2
        )
        with open(state_file, "w") as f:
            f.write("idle")

    print(f"{POD_NAME} finished hyper run {current}")
