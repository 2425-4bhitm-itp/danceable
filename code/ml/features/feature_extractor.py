import librosa
import numpy as np

class AudioFeatureExtractor:
    def __init__(self, sr=22050, n_mfcc=13, n_fft=2048, hop_length=512):
        self.sr = sr
        self.n_mfcc = n_mfcc
        self.n_fft = n_fft
        self.hop_length = hop_length

    def load_audio(self, file_path):
        """Load and normalize an audio file."""
        y, sr = librosa.load(file_path, sr=self.sr)
        y = librosa.util.normalize(y)
        return y, sr

    def extract_features(self, y):
        features = {}

        # --- MFCCs ---
        mfccs = librosa.feature.mfcc(
            y=y, sr=self.sr, n_mfcc=self.n_mfcc,
            n_fft=self.n_fft, hop_length=self.hop_length
        )
        for i, (mean, var) in enumerate(zip(np.mean(mfccs, axis=1), np.var(mfccs, axis=1))):
            features[f"mfcc_{i+1}_mean"] = mean
            features[f"mfcc_{i+1}_var"] = var

        # --- Chroma ---
        chroma = librosa.feature.chroma_stft(
            y=y, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length
        )
        for i, (mean, var) in enumerate(zip(np.mean(chroma, axis=1), np.var(chroma, axis=1))):
            features[f"chroma_{i+1}_mean"] = mean
            features[f"chroma_{i+1}_var"] = var

        # --- Mel Spectrogram ---
        mel = librosa.feature.melspectrogram(
            y=y, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length
        )
        for i, (mean, var) in enumerate(zip(np.mean(mel, axis=1), np.var(mel, axis=1))):
            features[f"mel_{i+1}_mean"] = mean
            features[f"mel_{i+1}_var"] = var

        # --- Spectral Contrast ---
        contrast = librosa.feature.spectral_contrast(
            y=y, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length
        )
        for i, (mean, var) in enumerate(zip(np.mean(contrast, axis=1), np.var(contrast, axis=1))):
            features[f"contrast_{i+1}_mean"] = mean
            features[f"contrast_{i+1}_var"] = var

        # --- Tonnetz ---
        tonnetz = librosa.feature.tonnetz(
            y=librosa.effects.harmonic(y), sr=self.sr
        )
        for i, (mean, var) in enumerate(zip(np.mean(tonnetz, axis=1), np.var(tonnetz, axis=1))):
            features[f"tonnetz_{i+1}_mean"] = mean
            features[f"tonnetz_{i+1}_var"] = var

        # --- Tempogram (rhythmic periodicity) ---
        tempogram = librosa.feature.tempogram(y=y, sr=self.sr, hop_length=self.hop_length)
        tempogram_mean = np.mean(tempogram, axis=1)
        tempogram_var = np.var(tempogram, axis=1)
        for i, (mean, var) in enumerate(zip(tempogram_mean, tempogram_var)):
            features[f"tempogram_{i+1}_mean"] = mean
            features[f"tempogram_{i+1}_var"] = var

        # --- RMS Energy ---
        rms = librosa.feature.rms(y=y)
        features["rms_mean"] = float(np.mean(rms))
        features["rms_var"] = float(np.var(rms))

        # --- Spectral Flux ---
        spectral_flux = np.sqrt(np.mean(np.diff(librosa.feature.melspectrogram(
            y=y, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length
        ), axis=1) ** 2, axis=1))
        features["spectral_flux_mean"] = float(np.mean(spectral_flux))
        features["spectral_flux_var"] = float(np.var(spectral_flux))

        # --- Onset Strength ---
        onset_env = librosa.onset.onset_strength(y=y, sr=self.sr)
        features["onset_strength_mean"] = float(np.mean(onset_env))
        features["onset_strength_var"] = float(np.var(onset_env))

        # --- Tempo (global BPM estimate) ---
        tempo, _ = librosa.beat.beat_track(y=y, sr=self.sr)
        features["tempo_bpm"] = float(tempo)

        return features

    def extract_features_from_file(self, file_path):
        y, sr = self.load_audio(file_path)
        return self.extract_features(y)
