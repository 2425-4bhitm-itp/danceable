import os
import csv
from concurrent.futures import ThreadPoolExecutor

class AudioDatasetCreator:
    def __init__(self, extractor, output_csv="/app/song-storage/features.csv"):
        self.extractor = extractor
        self.output_csv = output_csv
        self.header_written = False

    def process_folder(self, folder_path, label):
        """Extract features from all WAV files in a folder and save them with labels."""
        print(f"processing folder {folder_path}")
        data = []

        def process_file(file):
            if file.endswith(".wav"):
                file_path = os.path.join(folder_path, file)
                features = self.extractor.extract_features_from_file(file_path)
                return [file] + list(features) + [label]
            return None

        worker_amount = os.cpu_count() - 2

        with ThreadPoolExecutor(max_workers=worker_amount) as executor:
            results = executor.map(process_file, os.listdir(folder_path))

        for result in results:
            if result:
                data.append(result)

        self.save_to_csv(data)

    def save_to_csv(self, data):
        """Save extracted features to a CSV file."""
        with open(self.output_csv, "a", newline="") as f:
            writer = csv.writer(f)
            if not self.header_written:
                header = ["filename"] + [f"feature_{i}" for i in range(len(data[0]) - 2)] + ["label"]
                writer.writerow(header)
                self.header_written = True
            writer.writerows(data)

    def upload_single_file(self, file_path, label):
        """Extract features from a single WAV file and save them with a label."""
        features = self.extractor.extract_features_from_file(file_path)
        data = [[os.path.basename(file_path)] + list(features) + [label]]
        self.save_to_csv(data)