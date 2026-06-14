import logging

import numpy as np

from backend.app.services.audio_preprocessor import PreprocessedAudio
from ml_pipeline.preprocessing.feature_extraction import extract_mel_spectrogram, extract_mfcc

LOGGER = logging.getLogger(__name__)


class FeatureExtractor:
    def extract(self, audio: PreprocessedAudio) -> dict[str, np.ndarray]:
        LOGGER.info("[Feature Extraction Started] sample_rate=%s", audio.sample_rate)
        mel = extract_mel_spectrogram(audio.waveform)
        mfcc = extract_mfcc(audio.waveform)
        LOGGER.info("[Feature Extraction Complete] mel_shape=%s mfcc_shape=%s", mel.shape, mfcc.shape)
        return {"mel_spectrogram": mel, "mfcc": mfcc}
