from concurrent.futures import ThreadPoolExecutor
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
        def compute_mfccs():
            mfccs = librosa.feature.mfcc(y=y, sr=self.sr, n_mfcc=self.n_mfcc, n_fft=self.n_fft, hop_length=self.hop_length)
            return np.mean(mfccs, axis=1), np.var(mfccs, axis=1)

        def compute_chroma():
            chroma = librosa.feature.chroma_stft(y=y, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length)
            return np.mean(chroma, axis=1), np.var(chroma, axis=1)

        def compute_mel():
            mel = librosa.feature.melspectrogram(y=y, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length)
            return np.mean(mel, axis=1), np.var(mel, axis=1)

        def compute_contrast():
            contrast = librosa.feature.spectral_contrast(y=y, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length)
            return np.mean(contrast, axis=1), np.var(contrast, axis=1)

        def compute_tonnetz():
            tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=self.sr)
            return np.mean(tonnetz, axis=1), np.var(tonnetz, axis=1)

        def compute_tempogram():
            tempogram = librosa.feature.tempogram(y=y, sr=self.sr, hop_length=self.hop_length)
            return np.mean(tempogram, axis=1), np.var(tempogram, axis=1)

        # Multithreading for parallel feature computation
        with ThreadPoolExecutor() as executor:
            mfccs_result = executor.submit(compute_mfccs)
            chroma_result = executor.submit(compute_chroma)
            mel_result = executor.submit(compute_mel)
            contrast_result = executor.submit(compute_contrast)
            tonnetz_result = executor.submit(compute_tonnetz)
            tempogram_result = executor.submit(compute_tempogram)

            # Wait for results
            mfccs_mean, mfccs_var = mfccs_result.result()
            chroma_mean, chroma_var = chroma_result.result()
            mel_mean, mel_var = mel_result.result()
            contrast_mean, contrast_var = contrast_result.result()
            tonnetz_mean, tonnetz_var = tonnetz_result.result()
            tempogram_mean, tempogram_var = tempogram_result.result()

        # Concatenate all features
        features = np.concatenate([
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
