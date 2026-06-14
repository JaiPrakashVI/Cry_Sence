import logging
from pathlib import Path

import soundfile as sf
import librosa
from fastapi import HTTPException, UploadFile, status

from backend.app.models.audio import AudioMetadata
from backend.app.utils.config import get_settings

LOGGER = logging.getLogger(__name__)

SUPPORTED_CONTENT_TYPES = {
    "audio/wav",
    "audio/wave",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
    "audio/webm",
    "audio/flac",
    "application/octet-stream"
}

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".mp4", ".webm", ".flac", ".ogg"}


def validate_upload_metadata(file: UploadFile) -> None:
    settings = get_settings()
    content_type = file.content_type or "application/octet-stream"
    suffix = Path(file.filename or "").suffix.lower()

    LOGGER.info("[Audio Upload] filename=%s content_type=%s", file.filename, content_type)
    if content_type not in SUPPORTED_CONTENT_TYPES and suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported audio format '{content_type}'. Use WAV, MP3, M4A, WebM, FLAC, or OGG."
        )

    max_bytes = settings.max_upload_mb * 1024 * 1024
    if file.size is not None and file.size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file exceeds {settings.max_upload_mb} MB."
        )


def validate_saved_file(path: Path, original_filename: str, content_type: str) -> AudioMetadata:
    if not path.exists():
        raise HTTPException(status_code=500, detail="Uploaded audio was not saved.")

    size_bytes = path.stat().st_size
    if size_bytes <= 0:
        raise HTTPException(status_code=400, detail="Uploaded audio is empty.")

    try:
        info = sf.info(str(path))
        duration = float(info.duration)
        sample_rate = int(info.samplerate)
        channels = int(info.channels)
    except Exception as exc:
        LOGGER.warning("[Audio Validation] soundfile could not read %s; trying librosa. error=%s", path, exc)
        try:
            audio, sample_rate = librosa.load(str(path), sr=None, mono=False)
            duration = float(librosa.get_duration(y=audio, sr=sample_rate))
            channels = int(audio.shape[0]) if getattr(audio, "ndim", 1) > 1 else 1
        except Exception as decode_exc:
            LOGGER.exception("[Audio Validation] decoder could not read %s", path)
            raise HTTPException(
                status_code=422,
                detail="Audio file could not be decoded. Try WAV, MP3, M4A, WebM, FLAC, or OGG."
            ) from decode_exc

    if duration <= 0:
        raise HTTPException(status_code=422, detail="Audio duration must be greater than 0 seconds.")

    LOGGER.info(
        "[Audio Validation] duration=%.3fs sample_rate=%s channels=%s size=%s",
        duration,
        sample_rate,
        channels,
        size_bytes
    )
    return AudioMetadata(
        path=path,
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=size_bytes,
        duration_seconds=duration,
        sample_rate=sample_rate,
        channels=channels
    )
