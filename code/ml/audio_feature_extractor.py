import librosa
import numpy as np

class AudioFeatureExtractor:
    def __init__(self, sr=22050, n_mfcc=13, n_fft=2048, hop_length=512):
        self.sr = sr
        self.n_mfcc = n_mfcc
        self.n_fft = n_fft
        self.hop_length = hop_length

    def load_audio(self, file_path):
        y, sr = librosa.load(file_path, sr=self.sr)
        return y, sr

    def extract_features(self, y):
        # Compute MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=self.sr, n_mfcc=self.n_mfcc, n_fft=self.n_fft, hop_length=self.hop_length)
        mfccs_mean = np.mean(mfccs, axis=1)
        mfccs_var = np.var(mfccs, axis=1)

        # Compute Chroma feature
        chroma = librosa.feature.chroma_stft(y=y, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length)
        chroma_mean = np.mean(chroma, axis=1)
        chroma_var = np.var(chroma, axis=1)

        # Compute Mel-scaled spectrogram
        mel = librosa.feature.melspectrogram(y=y, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length)
        mel_mean = np.mean(mel, axis=1)
        mel_var = np.var(mel, axis=1)

        # Compute Spectral Contrast
        contrast = librosa.feature.spectral_contrast(y=y, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length)
        contrast_mean = np.mean(contrast, axis=1)
        contrast_var = np.var(contrast, axis=1)

        # Compute Tonnetz
        tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=self.sr)
        tonnetz_mean = np.mean(tonnetz, axis=1)
        tonnetz_var = np.var(tonnetz, axis=1)

        # Compute Tempogram
        tempogram = librosa.feature.tempogram(y=y, sr=self.sr, hop_length=self.hop_length)
        tempogram_mean = np.mean(tempogram, axis=1)
        tempogram_var = np.var(tempogram, axis=1)

        features_array = np.concatenate([
            mfccs_mean, mfccs_var,
            chroma_mean, chroma_var,
            mel_mean, mel_var,
            contrast_mean, contrast_var,
            tonnetz_mean, tonnetz_var,
            tempogram_mean, tempogram_var
        ])

        return features

    def extract_features_from_file(self, file_path):
        y, sr = self.load_audio(file_path)
        return self.extract_features(y)
