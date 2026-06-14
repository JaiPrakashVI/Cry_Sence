from fastapi import APIRouter

from backend.app.models.audio import ModelHealthResponse
from backend.app.models.schemas import HealthResponse
from backend.app.services.inference_service import InferenceService
from backend.app.utils.config import get_settings

router = APIRouter(tags=["system"])
settings = get_settings()
inference_service = InferenceService(settings.model_path)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="crysense-api", environment=settings.environment)


@router.get("/model-info")
async def model_info():
    return inference_service.model_info()


@router.get("/model-health", response_model=ModelHealthResponse)
async def model_health() -> ModelHealthResponse:
    return ModelHealthResponse(
        status=inference_service.status,
        model_loaded=inference_service.model is not None,
        model_path=str(inference_service.model_path),
        fallback_enabled=True
    )
