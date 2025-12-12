import json
import os
from pathlib import Path
from audio_processor import process_single_audio

TASK_FILE = "/app/tasks.json"

def load_tasks():
    path = Path(TASK_FILE)
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)

def slice_for_worker(tasks, index, total):
    n = len(tasks)
    size = n // total
    rem = n % total
    start = index * size + min(index, rem)
    end = start + size + (1 if index < rem else 0)
    return tasks[start:end]

def run_worker():
    index = int(os.environ.get("JOB_COMPLETION_INDEX", "0"))
    total = int(os.environ.get("JOB_PARALLELISM", "1"))
    tasks = load_tasks()
    shard = slice_for_worker(tasks, index, total)
    for file_path, label in shard:
        process_single_audio(file_path, label)

if __name__ == "__main__":
    run_worker()
