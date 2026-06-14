from dataclasses import dataclass

import librosa
import numpy as np


@dataclass(frozen=True)
class AudioConfig:
    sample_rate: int = 22050
    duration_seconds: int = 5
    top_db: int = 30

    @property
    def target_samples(self) -> int:
        return self.sample_rate * self.duration_seconds


def load_audio(path: str, config: AudioConfig = AudioConfig()) -> np.ndarray:
    audio, _ = librosa.load(path, sr=config.sample_rate, mono=True)
    audio, _ = librosa.effects.trim(audio, top_db=config.top_db)
    return pad_or_trim(normalize_audio(audio), config.target_samples)


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(audio)) if audio.size else 0
    if peak == 0:
        return audio.astype(np.float32)
    return (audio / peak).astype(np.float32)


def pad_or_trim(audio: np.ndarray, target_samples: int) -> np.ndarray:
    if len(audio) > target_samples:
        return audio[:target_samples]
    return np.pad(audio, (0, target_samples - len(audio))).astype(np.float32)


def reduce_noise_spectral_gate(audio: np.ndarray, noise_floor_percentile: int = 20) -> np.ndarray:
    spectrum = np.fft.rfft(audio)
    magnitude = np.abs(spectrum)
    threshold = np.percentile(magnitude, noise_floor_percentile)
    spectrum[magnitude < threshold] = 0
    return np.fft.irfft(spectrum, n=len(audio)).astype(np.float32)
