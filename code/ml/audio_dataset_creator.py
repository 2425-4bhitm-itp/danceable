import os
import csv
import numpy as np

class AudioDatasetCreator:
    def __init__(self, extractor, output_csv="/app/song-storage/features.csv"):
        self.extractor = extractor
        self.output_csv = output_csv
        self.header_written = False

    def process_folder(self, folder_path, label):
        data = []

        for file in os.listdir(folder_path):
            if file.endswith(".wav"):
                file_path = os.path.join(folder_path, file)
                features = self.extractor.extract_features_from_file(file_path)
                features["filename"] = file
                features["label"] = label
                data.append(features)

        self.save_to_csv(data)

    def save_to_csv(self, data):
        """Save extracted features to a CSV file."""
        with open(self.output_csv, "a", newline="") as f:
            if data:  # Ensure there is data to write
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                if not self.header_written:
                    writer.writeheader()
                    self.header_written = True
                writer.writerows(data)

    def upload_single_file(self, file_path, label):
        """Extract features from a single WAV file and save them with a label."""
        features = self.extractor.extract_features_from_file(file_path)
        features["filename"] = os.path.basename(file_path)
        features["label"] = label
        self.save_to_csv([features])