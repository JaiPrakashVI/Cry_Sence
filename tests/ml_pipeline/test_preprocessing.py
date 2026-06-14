import numpy as np

from ml_pipeline.preprocessing.audio_preprocessing import normalize_audio, pad_or_trim


def test_normalize_audio_scales_peak_to_one():
    audio = np.array([0.0, 2.0, -4.0], dtype=np.float32)
    normalized = normalize_audio(audio)
    assert np.max(np.abs(normalized)) == 1.0


def test_pad_or_trim_returns_target_length():
    audio = np.array([1.0, 2.0], dtype=np.float32)
    padded = pad_or_trim(audio, 5)
    assert len(padded) == 5
