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
        target_time_bins=128
    ):
        self.sr = sr
        self.window_seconds = window_seconds
        self.window_len = window_seconds * sr
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.target_time_bins = target_time_bins

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

    def _normalize(self, x):
        return (x - x.mean()) / (x.std() + 1e-8)

    def _fix_time_axis(self, x):
        return librosa.util.fix_length(x, size=self.target_time_bins, axis=1)

    def _mel(self, y):
        mel = librosa.feature.melspectrogram(
            y=y,
            sr=self.sr,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mels=self.n_mels
        )
        mel = librosa.power_to_db(mel)
        mel = self._normalize(mel)
        mel = self._fix_time_axis(mel)
        return mel.astype(np.float32)

    def _mfcc(self, y, n_mfcc=40):
        mf = librosa.feature.mfcc(
            y=y,
            sr=self.sr,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mfcc=n_mfcc
        )
        mf = self._normalize(mf)
        mf = self._fix_time_axis(mf)
        return mf.astype(np.float32)

    def _chroma(self, y):
        chroma = librosa.feature.chroma_cqt(
            y=y,
            sr=self.sr
        )
        chroma = self._normalize(chroma)
        chroma = self._fix_time_axis(chroma)
        return chroma.astype(np.float32)

    def _spectral_contrast(self, y):
        sc = librosa.feature.spectral_contrast(
            y=y,
            sr=self.sr,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        sc = self._normalize(sc)
        sc = self._fix_time_axis(sc)
        return sc.astype(np.float32)

    def _tempogram(self, y):
        tgram = librosa.feature.tempogram(
            y=y,
            sr=self.sr,
            hop_length=self.hop_length
        )
        tgram = self._normalize(tgram)
        tgram = self._fix_time_axis(tgram)
        return tgram.astype(np.float32)

    def _onset(self, y):
        on = librosa.onset.onset_strength(
            y=y,
            sr=self.sr,
            hop_length=self.hop_length
        )
        on = on[np.newaxis, :]
        on = self._normalize(on)
        on = self._fix_time_axis(on)
        return on.astype(np.float32)

    def _combine_features(self, feats):
        stacked = np.concatenate(
            [f[np.newaxis, ...] for f in feats],
            axis=0
        )
        return stacked

    def extract_features_from_file(self, path):
        y = self.load_audio(path)
        windows = self.slice_into_windows(y)

        outputs = []
        for w in windows:
            mel = self._mel(w)
            mfcc = self._mfcc(w)
            chroma = self._chroma(w)
            spec_contrast = self._spectral_contrast(w)
            tempogram = self._tempogram(w)
            onset = self._onset(w)

            combined = self._combine_features(
                [mel, mfcc, chroma, spec_contrast, tempogram, onset]
            )
            outputs.append(combined)
        return outputs

    def wav_to_spectrogram_tensor(self, file_path):
        feats = self.extract_features_from_file(file_path)
        return feats[0]
