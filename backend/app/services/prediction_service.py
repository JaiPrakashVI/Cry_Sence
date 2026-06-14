import logging
from pathlib import Path

from backend.app.models.audio import AudioMetadata
from backend.app.models.schemas import PredictionResponse
from backend.app.services.audio_converter import AudioConverter
from backend.app.services.audio_preprocessor import AudioPreprocessor
from backend.app.services.feature_extractor import FeatureExtractor

LOGGER = logging.getLogger(__name__)


class PredictionService:
    def __init__(self, inference_service) -> None:
        self.inference_service = inference_service
        self.converter = AudioConverter()
        self.preprocessor = AudioPreprocessor()
        self.extractor = FeatureExtractor()

    def analyze(self, metadata: AudioMetadata, trace_id: str) -> PredictionResponse:
        LOGGER.info("[Inference Started] trace_id=%s", trace_id)
        try:
            wav_path = self.converter.convert_to_wav(metadata.path)
            preprocessed = self.preprocessor.preprocess(wav_path)
            features = self.extractor.extract(preprocessed)
            prediction = self.inference_service.predict_features(features, wav_path)
            LOGGER.info("[Prediction Generated] trace_id=%s emotion=%s", trace_id, prediction.emotion)
        except Exception:
            LOGGER.exception("[Inference Failed] trace_id=%s; using feature-aware fallback", trace_id)
            prediction = self._fallback(metadata.path)

        prediction.trace_id = trace_id
        prediction.audio_details = {
            "filename": metadata.original_filename,
            "content_type": metadata.content_type,
            "size_bytes": metadata.size_bytes,
            "duration_seconds": round(metadata.duration_seconds, 3),
            "sample_rate": metadata.sample_rate,
            "channels": metadata.channels
        }
        LOGGER.info("[Response Sent] trace_id=%s", trace_id)
        return prediction

    def _fallback(self, audio_path: Path) -> PredictionResponse:
        return self.inference_service.fallback_prediction(audio_path)
