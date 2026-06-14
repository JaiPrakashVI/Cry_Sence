import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ml_pipeline.preprocessing.audio_preprocessing import AudioConfig, load_audio, reduce_noise_spectral_gate

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreprocessedAudio:
    waveform: np.ndarray
    sample_rate: int
    duration_seconds: float


class AudioPreprocessor:
    def __init__(self, config: AudioConfig = AudioConfig()) -> None:
        self.config = config

    def preprocess(self, path: Path) -> PreprocessedAudio:
        LOGGER.info("[Preprocessing Started] path=%s", path.name)
        waveform = load_audio(str(path), self.config)
        waveform = reduce_noise_spectral_gate(waveform)
        if waveform.size == 0 or not np.any(np.abs(waveform) > 1e-6):
            raise ValueError("Audio waveform is empty or silent after preprocessing.")
        duration = len(waveform) / self.config.sample_rate
        LOGGER.info("[Preprocessing Complete] samples=%s duration=%.3fs", len(waveform), duration)
        return PreprocessedAudio(waveform=waveform, sample_rate=self.config.sample_rate, duration_seconds=duration)
