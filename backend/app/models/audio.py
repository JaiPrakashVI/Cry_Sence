from pathlib import Path

from pydantic import BaseModel, Field


class AudioMetadata(BaseModel):
    path: Path
    original_filename: str
    content_type: str
    size_bytes: int = Field(gt=0)
    duration_seconds: float = Field(ge=0)
    sample_rate: int = Field(gt=0)
    channels: int = Field(gt=0)


class AudioHealthResponse(BaseModel):
    status: str
    supported_content_types: list[str]
    max_upload_mb: int
    converter: str


class ModelHealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str
    fallback_enabled: bool
