import librosa
import numpy as np

class AudioFeatureExtractorCNN:
    def __init__(
        self,
        sr=22050,
        window_seconds=3,
        n_fft=1024,
        hop_length=256,
        n_mels=128,
    ):
        self.sr = sr
        self.window_seconds = window_seconds
        self.window_len = window_seconds * sr
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels

    def load_audio(self, file_path):
        y, _ = librosa.load(file_path, sr=self.sr)
        y = librosa.util.normalize(y)
        return y

    def slice_into_windows(self, y):
        windows = []
        step = self.window_len
        total = len(y)
        for start in range(0, total - self.window_len + 1, step):
            end = start + self.window_len
            windows.append(y[start:end])
        return windows

    def mel_patch(self, y_window):
        mel = librosa.feature.melspectrogram(
            y=y_window,
            sr=self.sr,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mels=self.n_mels,
        )
        mel = librosa.power_to_db(mel, ref=np.max)
        mel_norm = (mel - mel.mean()) / (mel.std() + 1e-8)
        mel_resized = librosa.util.fix_length(mel_norm, size=128, axis=1)
        return mel_resized.astype(np.float32)

    def extract_features_from_file(self, path):
        y = self.load_audio(path)
        windows = self.slice_into_windows(y)
        mel_patches = [self.mel_patch(w) for w in windows]
        return mel_patches

    def wav_to_spectrogram_tensor(self, file_path):
        y = self.load_audio(file_path)
        mel_spec = librosa.feature.melspectrogram(
            y=y, sr=self.sr, n_mels=self.n_mels,
            n_fft=self.n_fft, hop_length=self.hop_length
        )
        log_spec = librosa.power_to_db(mel_spec)
        # Normalize to 0-1
        log_spec -= log_spec.min()
        log_spec /= (log_spec.max() + 1e-6)
        # Add channel dimension
        return log_spec[np.newaxis, ..., np.newaxis]