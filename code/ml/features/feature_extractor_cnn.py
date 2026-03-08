import warnings
import librosa
import numpy as np

warnings.filterwarnings("ignore", message="PySoundFile failed")
warnings.filterwarnings("ignore", category=FutureWarning, module="librosa")

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

    def load_audio(self, file_path, should_print_duration=False):
        y, sr = librosa.load(file_path, sr=self.sr)

        if y is None or len(y) == 0:
            raise ValueError("Audio decode failed")

        if should_print_duration:
            duration = len(y) / sr
            print("AUDIO DURATION:", duration)

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

    def simulate_phone_recording(self, y, sr=22050):
        """
        Apply phone-like degradation to a studio waveform.
        Tuned against real phone recording analysis:
        - Real phone spectral centroid ~214Hz (studio: 891Hz) -> very aggressive low-pass
        - Real phone 85% energy rolloff at ~290Hz (studio: 1571Hz)
        - Real phone is clean (SNR ~52dB) -> minimal noise
        - ZCR slightly higher on phone -> mild room reverb
        """
        freqs = np.fft.rfftfreq(len(y), d=1 / sr)

        # 1. Aggressive low-pass with gradual shelf
        #    Full pass below 300Hz, shelf down to 0.05 by 1kHz, near-silence above
        F = np.fft.rfft(y)
        gain = np.ones(len(freqs), dtype=np.float32)
        shelf_mask = (freqs >= 300) & (freqs < 1000)
        gain[shelf_mask] = np.linspace(1.0, 0.05, shelf_mask.sum())
        gain[freqs >= 1000] = 0.02
        F *= gain
        y = np.fft.irfft(F, n=len(y))

        # 2. Strong low-frequency resonance boost (phone body/room)
        #    Peak below ~120Hz, much stronger than before
        F = np.fft.rfft(y)
        freqs = np.fft.rfftfreq(len(y), d=1 / sr)
        boost = 1.0 + 3.0 * np.exp(-freqs / 120)
        F *= boost
        y = np.fft.irfft(F, n=len(y))

        # 3. Mild room reverb - early reflection at ~18ms
        #    Accounts for higher ZCR on real phone recording
        delay_samples = int(0.018 * sr)
        reverb_tail = np.zeros_like(y)
        reverb_tail[delay_samples:] = y[:-delay_samples] * 0.18
        y = y + reverb_tail

        # 4. Very light noise floor - real phone is clean, just a hint
        noise_level = 0.0005
        noise = np.random.normal(0, noise_level, size=y.shape)
        y = y + noise

        # 5. Mild AGC / soft clip
        threshold = 0.75
        y = np.where(
            np.abs(y) > threshold,
            np.sign(y) * (threshold + (np.abs(y) - threshold) * 0.25),
            y
        )

        # 6. Scale down ~6dB to match real phone recording level, then normalize
        y *= 0.5
        y = librosa.util.normalize(y)

        return y

    def extract_features_from_file(self, path, simulate_phone=False, should_print_duration=False):
        y = self.load_audio(path, should_print_duration)

        if simulate_phone:
            y = self.simulate_phone_recording(y, sr=self.sr)

        windows = self.slice_into_windows(y)
        outputs = []
        if len(y) < len(windows):
            raise ValueError("Audio too short for feature extraction")

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
