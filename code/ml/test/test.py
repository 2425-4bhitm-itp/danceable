import itertools
import json
import uuid
from datetime import datetime
from pathlib import Path

import tensorflow as tf

from training.model_cnn import train_model, build_cnn


def run_experiment(config: dict) -> dict:
    message = train_model(
        batch_size=config["batch_size"],
        epochs=config["epochs"],
        model_config=config
    )

    return {
        "filters": config["filters"],
        "dense_units": config["dense_units"],
        "dropout_rate": config["dropout_rate"],
        "learning_rate": config["learning_rate"],
        "batch_size": config["batch_size"],
        "test_loss": message["loss"],
        "test_accuracy": message["accuracy"]
    }


def main():
    search_space = {
        "filters": [
            (32, 64, 128),
            (32, 64)
        ],
        "dense_units": [128, 256],
        "dropout_rate": [0.3, 0.5],
        "learning_rate": [1e-3, 3e-4],
        "batch_size": [32, 64],
        "epochs": [100]
    }

    keys = list(search_space.keys())
    runs = list(itertools.product(*search_space.values()))

    log_dir = Path("cnn_runs")
    log_dir.mkdir(exist_ok=True)

    results = []

    for values in runs:
        config = dict(zip(keys, values))
        run_id = uuid.uuid4().hex[:8]
        timestamp = datetime.utcnow().isoformat()

        tf.keras.backend.clear_session()

        result = run_experiment(config)
        result["run_id"] = run_id
        result["timestamp"] = timestamp

        results.append(result)

        with open(log_dir / f"run_{run_id}.json", "w") as f:
            json.dump(result, f, indent=2)

    with open(log_dir / "summary.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
