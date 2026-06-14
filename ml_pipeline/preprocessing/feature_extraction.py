import librosa
import numpy as np

from ml_pipeline.preprocessing.audio_preprocessing import AudioConfig, load_audio, reduce_noise_spectral_gate


def extract_mfcc(audio: np.ndarray, config: AudioConfig = AudioConfig(), n_mfcc: int = 40) -> np.ndarray:
    mfcc = librosa.feature.mfcc(y=audio, sr=config.sample_rate, n_mfcc=n_mfcc)
    return scale_feature(mfcc)


def extract_mel_spectrogram(
    audio: np.ndarray,
    config: AudioConfig = AudioConfig(),
    n_mels: int = 128,
    target_frames: int = 128
) -> np.ndarray:
    mel = librosa.feature.melspectrogram(y=audio, sr=config.sample_rate, n_mels=n_mels)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_db = scale_feature(mel_db)
    return fit_time_axis(mel_db, target_frames)[..., np.newaxis]


def audio_file_to_spectrogram(path: str, config: AudioConfig = AudioConfig()) -> np.ndarray:
    audio = load_audio(path, config)
    audio = reduce_noise_spectral_gate(audio)
    return extract_mel_spectrogram(audio, config)


def scale_feature(feature: np.ndarray) -> np.ndarray:
    mean = np.mean(feature)
    std = np.std(feature)
    if std == 0:
        return feature.astype(np.float32)
    return ((feature - mean) / std).astype(np.float32)


def fit_time_axis(feature: np.ndarray, target_frames: int) -> np.ndarray:
    if feature.shape[1] > target_frames:
        return feature[:, :target_frames]
    return np.pad(feature, ((0, 0), (0, target_frames - feature.shape[1]))).astype(np.float32)
