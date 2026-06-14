from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    distress_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    emotion: str
    risk_category: str
    summary: str
    trace_id: str | None = None
    audio_details: dict = Field(default_factory=dict)
    emotion_distribution: dict[str, float] = Field(default_factory=dict)


class ModelInfo(BaseModel):
    name: str
    version: str
    classes: list[str]
    input_shape: tuple[int, int, int]
    status: str


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
