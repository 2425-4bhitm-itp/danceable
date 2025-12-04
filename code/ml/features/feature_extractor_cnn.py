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
        n_mfcc=40,
        target_time_bins=128,
        target_height=128
    ):
        self.sr = sr
        self.window_seconds = window_seconds
        self.window_len = int(window_seconds * sr)
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.n_mfcc = n_mfcc
        self.target_time_bins = target_time_bins
        self.target_height = target_height

    def load_audio(self, file_path):
        y, _ = librosa.load(file_path, sr=self.sr)
        return librosa.util.normalize(y)

    def slice_into_windows(self, y):
        return [y[i:i+self.window_len] for i in range(0, len(y)-self.window_len+1, self.window_len)]

    def _normalize(self, x):
        return (x - x.mean()) / (x.std() + 1e-8)

    def _fix_shape(self, x):
        # Fix height and time axes
        x = librosa.util.fix_length(x, size=self.target_height, axis=0)
        x = librosa.util.fix_length(x, size=self.target_time_bins, axis=1)
        return x

    def _extract_mel(self, y):
        mel = librosa.feature.melspectrogram(y=y, sr=self.sr, n_fft=self.n_fft,
                                             hop_length=self.hop_length, n_mels=self.n_mels)
        mel = librosa.power_to_db(mel)
        mel = self._normalize(mel)
        return self._fix_shape(mel).astype(np.float32)

    def _extract_mfcc(self, y):
        mfcc = librosa.feature.mfcc(y=y, sr=self.sr, n_mfcc=self.n_mfcc,
                                    n_fft=self.n_fft, hop_length=self.hop_length)
        mfcc = self._normalize(mfcc)
        return self._fix_shape(mfcc).astype(np.float32)

    def _extract_chroma(self, y):
        chroma = librosa.feature.chroma_cqt(y=y, sr=self.sr)
        chroma = self._normalize(chroma)
        return self._fix_shape(chroma).astype(np.float32)

    def _extract_spectral_contrast(self, y):
        sc = librosa.feature.spectral_contrast(y=y, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length)
        sc = self._normalize(sc)
        return self._fix_shape(sc).astype(np.float32)

    def _extract_tempogram(self, y):
        tgram = librosa.feature.tempogram(y=y, sr=self.sr, hop_length=self.hop_length)
        tgram = self._normalize(tgram)
        return self._fix_shape(tgram).astype(np.float32)

    def _extract_onset(self, y):
        on = librosa.onset.onset_strength(y=y, sr=self.sr, hop_length=self.hop_length)
        on = on[np.newaxis, :]
        on = self._normalize(on)
        return self._fix_shape(on).astype(np.float32)

    def _combine_features(self, feats):
        # stack along channel axis: H x W x C
        return np.stack(feats, axis=-1)

    def extract_features_from_file(self, path):
        y = self.load_audio(path)
        windows = self.slice_into_windows(y)
        outputs = []

        for w in windows:
            mel = self._extract_mel(w)
            mfcc = self._extract_mfcc(w)
            chroma = self._extract_chroma(w)
            sc = self._extract_spectral_contrast(w)
            tgram = self._extract_tempogram(w)
            onset = self._extract_onset(w)

            combined = self._combine_features([mel, mfcc, chroma, sc, tgram, onset])
            outputs.append(combined)

        return outputs

    def wav_to_spectrogram_tensor(self, file_path):
        feats = self.extract_features_from_file(file_path)
        return feats[0]
