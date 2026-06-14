import logging
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.app.models.audio import AudioHealthResponse
from backend.app.models.schemas import PredictionResponse
from backend.app.routes.health import inference_service
from backend.app.services.audio_validation import SUPPORTED_CONTENT_TYPES, validate_saved_file, validate_upload_metadata
from backend.app.services.prediction_service import PredictionService
from backend.app.services.storage_service import StorageService
from backend.app.utils.config import get_settings

router = APIRouter(tags=["audio"])
settings = get_settings()
storage = StorageService(settings.storage_dir)
prediction_service = PredictionService(inference_service)
LOGGER = logging.getLogger(__name__)


@router.post("/upload-audio", response_model=PredictionResponse)
async def upload_audio(file: UploadFile = File(...)) -> PredictionResponse:
    return await analyze(file)


@router.post("/record-audio", response_model=PredictionResponse)
async def record_audio(file: UploadFile = File(...)) -> PredictionResponse:
    return await analyze(file)


@router.post("/analyze", response_model=PredictionResponse)
async def analyze(file: UploadFile = File(...)) -> PredictionResponse:
    trace_id = uuid4().hex
    LOGGER.info("[API Received] trace_id=%s endpoint=/analyze filename=%s", trace_id, file.filename)
    try:
        validate_upload_metadata(file)
        audio_path = await storage.save_upload(file)
        LOGGER.info("[File Saved] trace_id=%s path=%s", trace_id, audio_path)
        metadata = validate_saved_file(
            audio_path,
            original_filename=file.filename or audio_path.name,
            content_type=file.content_type or "application/octet-stream"
        )
        return prediction_service.analyze(metadata, trace_id)
    except HTTPException:
        LOGGER.exception("[Audio Analysis Failed] trace_id=%s", trace_id)
        raise
    except Exception as exc:
        LOGGER.exception("[Audio Analysis Failed] trace_id=%s", trace_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio analysis failed for trace {trace_id}: {exc}"
        ) from exc


@router.get("/audio-health", response_model=AudioHealthResponse)
async def audio_health() -> AudioHealthResponse:
    return AudioHealthResponse(
        status="ok",
        supported_content_types=sorted(SUPPORTED_CONTENT_TYPES),
        max_upload_mb=settings.max_upload_mb,
        converter="librosa+soundfile wav normalization"
    )
