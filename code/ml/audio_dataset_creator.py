import os
import csv
import uuid
import librosa
import numpy as np
from pydub import AudioSegment
from scipy.signal import butter, lfilter
import soundfile as sf


def bandpass_filter(data, sr, low=300, high=3400):
    nyquist = 0.5 * sr
    b, a = butter(4, [low / nyquist, high / nyquist], btype='band')
    return lfilter(b, a, data)


def degrade_audio(input_path, output_path):
    try:
        audio, sr = sf.read(input_path)
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)  # Convert to mono

        filtered = bandpass_filter(audio, sr)

        if sr > 16000:
            audio = librosa.resample(filtered, orig_sr=sr, target_sr=16000)
            sr = 16000
        else:
            audio = filtered

        sf.write(output_path, audio, sr, subtype='PCM_16')

    except Exception as e:
        print(f"Error degrading audio {input_path}: {e}")

class AudioDatasetCreator:
    def __init__(self, extractor, output_csv="/app/song-storage/features.csv"):
        self.extractor = extractor
        self.output_csv = output_csv
        self.header_written = False
        self.temp_dir = "app/song-storage/tmp/audio_degrade"
        os.makedirs(self.temp_dir, exist_ok=True)

    def process_folder(self, folder_path, label):
        data = []

        for file in os.listdir(folder_path):
            if file.endswith(".wav"):
                file_path = os.path.join(folder_path, file)

                # Create unique filename to avoid collisions
                temp_filename = f"degraded_{uuid.uuid4().hex}.wav"
                degraded_file_path = os.path.join(self.temp_dir, temp_filename)

                #degrade_audio(file_path, degraded_file_path)

                features_array = self.extractor.extract_features_from_file(file_path)
                features = {f"feature_{i}": value for i, value in enumerate(features_array)}
                features["filename"] = file
                features["label"] = label
                data.append(features)

                try:
                    os.remove(degraded_file_path)
                except FileNotFoundError:
                    pass

        self.save_to_csv(data)

    def save_to_csv(self, data):
        """Save extracted features to a CSV file."""
        if not data:
            return

        with open(self.output_csv, "a", newline="") as f:
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
