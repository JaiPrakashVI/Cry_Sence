import logging
from pathlib import Path

import librosa
import soundfile as sf

LOGGER = logging.getLogger(__name__)


class AudioConverter:
    def __init__(self, target_sample_rate: int = 22050) -> None:
        self.target_sample_rate = target_sample_rate

    def convert_to_wav(self, source_path: Path) -> Path:
        destination = source_path.with_suffix(".normalized.wav")
        if destination.exists():
            return destination

        LOGGER.info("[Audio Converter] source=%s destination=%s", source_path.name, destination.name)
        audio, _ = librosa.load(str(source_path), sr=self.target_sample_rate, mono=True)
        if audio.size == 0:
            raise ValueError("Decoded audio waveform is empty.")
        sf.write(str(destination), audio, self.target_sample_rate, subtype="PCM_16")
        return destination
