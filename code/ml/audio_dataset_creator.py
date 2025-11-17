import os
import csv
import concurrent.futures
import pandas as pd
from paths import BASE_DIR, FEATURES_CSV

class AudioDatasetCreator:
    def __init__(self, extractor, output_csv=BASE_DIR / FEATURES_CSV):
        self.extractor = extractor
        self.output_csv = output_csv
        self.header_written = False

    def process_folder(self, folder_path, label):
        # Load already processed filenames
        if os.path.exists(self.output_csv) and os.path.getsize(self.output_csv) > 0:
            try:
                existing = pd.read_csv(self.output_csv)
                processed_files = set(existing["filename"].astype(str))
            except Exception:
                processed_files = set()
        else:
            processed_files = set()

        # Find files in folder that are not yet processed
        all_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".wav")]
        files = [f for f in all_files if f not in processed_files]

        if not files:
            print(f"All WAV files in folder already processed: {folder_path}")
            return

        print(f"Processing {len(files)} new files in {folder_path}")

        def process_file(file):
            path = os.path.join(folder_path, file)
            features_dict = self.extractor.extract_features_from_file(path)
            features_dict["filename"] = file
            features_dict["label"] = label
            return features_dict

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_file, files))

        self.save_to_csv(results)

    def save_to_csv(self, data):
        if not data:
            return

        # Ensure consistent field order: feature keys first, then metadata
        fieldnames = list(data[0].keys())
        # Optionally, move filename and label to the end for better readability
        if "filename" in fieldnames:
            fieldnames.remove("filename")
            fieldnames.append("filename")
        if "label" in fieldnames:
            fieldnames.remove("label")
            fieldnames.append("label")

        with open(self.output_csv, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not self.header_written:
                writer.writeheader()
                self.header_written = True
            writer.writerows(data)

    def upload_single_file(self, file_path, label):
        features_dict = self.extractor.extract_features_from_file(file_path)
        features_dict["filename"] = os.path.basename(file_path)
        features_dict["label"] = label
        self.save_to_csv([features_dict])
