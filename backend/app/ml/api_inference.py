from pathlib import Path

from backend.app.services.inference_service import InferenceService


def analyze_audio_file(path: str, model_path: str):
    service = InferenceService(model_path)
    return service.predict(Path(path)).model_dump()
