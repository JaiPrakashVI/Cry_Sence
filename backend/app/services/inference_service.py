import logging
from pathlib import Path

import numpy as np

from backend.app.models.schemas import ModelInfo, PredictionResponse

LOGGER = logging.getLogger(__name__)
EMOTION_CLASSES = ["Distress", "Crying", "Fear", "Panic", "Sadness", "Neutral", "Happy", "Angry"]
BABY_STATES = ["Hunger", "Pain", "Sleepy", "Discomfort", "Neutral"]


class InferenceService:
    def __init__(self, model_path: str) -> None:
        self.model_path = Path(model_path)
        self.model = None
        self.status = "fallback"
        self._load_model()

    def _load_model(self) -> None:
        if not self.model_path.exists():
            LOGGER.warning("Model not found at %s; using deterministic fallback.", self.model_path)
            return

        try:
            import tensorflow as tf

            self.model = tf.keras.models.load_model(self.model_path)
            self.status = "loaded"
        except Exception:
            LOGGER.exception("Failed to load model; using deterministic fallback.")

    def predict(self, audio_path: Path) -> PredictionResponse:
        if self.model is None:
            return self.fallback_prediction(audio_path)

        from ml_pipeline.inference.predict import predict_audio_file

        prediction = predict_audio_file(str(audio_path), self.model)
        return PredictionResponse(**prediction)

    def predict_features(self, features: dict, audio_path: Path) -> PredictionResponse:
        if self.model is None:
            return self.fallback_prediction(audio_path)

        import librosa
        # Load raw wav data for DSP feature extraction
        try:
            raw_data, sr = librosa.load(str(audio_path), sr=22050, mono=True)
        except Exception as e:
            LOGGER.warning(f"Failed to load raw audio for DSP features: {e}. Defaulting to zeros.")
            raw_data = np.zeros(110250)
            sr = 22050

        original_rms = float(np.sqrt(np.mean(raw_data ** 2))) if raw_data.size else 0.0
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=raw_data))) if raw_data.size else 0.0
        centroid = float(np.mean(librosa.feature.spectral_centroid(y=raw_data, sr=sr))) if raw_data.size else 0.0

        mel = features["mel_spectrogram"]
        probabilities = self.model.predict(np.expand_dims(mel, axis=0), verbose=0)[0]
        
        # 1. Map CNN probabilities to baby states
        # The model outputs alphabetical classes: ["Angry", "Crying", "Distress", "Fear", "Happy", "Neutral", "Panic", "Sadness"]
        cnn_baby_probs = np.zeros(5)
        # Pain: Panic (6), Crying (1), Distress (2), Fear (3)
        cnn_baby_probs[1] = probabilities[6] * 0.40 + probabilities[1] * 0.35 + probabilities[2] * 0.15 + probabilities[3] * 0.10
        # Hunger: Crying (1), Distress (2), Sadness (7), Neutral (5)
        cnn_baby_probs[0] = probabilities[1] * 0.40 + probabilities[2] * 0.40 + probabilities[7] * 0.15 + probabilities[5] * 0.05
        # Sleepy: Sadness (7), Neutral (5), Happy (4)
        cnn_baby_probs[2] = probabilities[7] * 0.50 + probabilities[5] * 0.40 + probabilities[4] * 0.10
        # Discomfort: Angry (0), Fear (3), Sadness (7), Neutral (5)
        cnn_baby_probs[3] = probabilities[0] * 0.45 + probabilities[3] * 0.35 + probabilities[7] * 0.15 + probabilities[5] * 0.05
        # Neutral: Neutral (5), Happy (4), Sadness (7)
        cnn_baby_probs[4] = probabilities[5] * 0.50 + probabilities[4] * 0.45 + probabilities[7] * 0.05

        # 2. Map DSP metrics to baby states heuristic distribution
        # Index map: 0=Hunger, 1=Pain, 2=Sleepy, 3=Discomfort, 4=Neutral
        dsp_baby_probs = np.zeros(5)
        if original_rms < 0.015:
            # Silence/Quiet -> Neutral, Sleepy
            dsp_baby_probs[4] = 0.75  # Neutral
            dsp_baby_probs[2] = 0.20  # Sleepy
            dsp_baby_probs[3] = 0.05  # Discomfort
        elif original_rms > 0.12:
            # Loud screaming/crying -> Pain, Hunger, Discomfort
            if zcr > 0.12 or centroid > 2400:
                dsp_baby_probs[1] = 0.70  # Pain
                dsp_baby_probs[0] = 0.15  # Hunger
                dsp_baby_probs[3] = 0.15  # Discomfort
            else:
                dsp_baby_probs[0] = 0.60  # Hunger
                dsp_baby_probs[1] = 0.20  # Pain
                dsp_baby_probs[3] = 0.20  # Discomfort
        else:
            # Medium levels -> Hunger, Discomfort, Sleepy, Neutral
            if zcr > 0.13 or centroid > 2100:
                dsp_baby_probs[0] = 0.50  # Hunger
                dsp_baby_probs[3] = 0.30  # Discomfort
                dsp_baby_probs[1] = 0.20  # Pain
            elif zcr > 0.075:
                dsp_baby_probs[3] = 0.50  # Discomfort
                dsp_baby_probs[2] = 0.30  # Sleepy
                dsp_baby_probs[4] = 0.20  # Neutral
            else:
                dsp_baby_probs[2] = 0.60  # Sleepy
                dsp_baby_probs[4] = 0.30  # Neutral
                dsp_baby_probs[3] = 0.10  # Discomfort

        # 3. Blend distributions (35% CNN + 65% DSP)
        blended_probs = 0.35 * cnn_baby_probs + 0.65 * dsp_baby_probs
        # Normalize
        blended_probs = blended_probs / (np.sum(blended_probs) or 1.0)

        class_index = int(np.argmax(blended_probs))
        confidence = float(blended_probs[class_index] * 100)
        baby_state = BABY_STATES[class_index]

        # Calculate distress score
        distress = self._distress_score(baby_state, confidence, blended_probs)
        # Adjust distress based on original raw RMS
        scaled_distress = min(100.0, max(5.0, distress * 0.4 + (original_rms * 250.0) + (zcr * 200.0)))

        LOGGER.info(f"[Inference Complete] Baby State: {baby_state} | Confidence: {confidence:.2f}% | Distress: {scaled_distress:.2f}%")

        distribution = {
            BABY_STATES[i]: round(float(blended_probs[i]) * 100, 2)
            for i in range(len(BABY_STATES))
        }

        summary = f"Identified baby feeling '{baby_state.lower()}' with {confidence:.1f}% confidence. Acoustic metrics: Volume RMS={original_rms:.3f}, Brightness={centroid:.0f}Hz."

        return PredictionResponse(
            distress_score=round(scaled_distress, 2),
            confidence_score=round(confidence, 2),
            emotion=baby_state,
            risk_category=self._risk_category(scaled_distress),
            summary=summary,
            emotion_distribution=distribution
        )

    def model_info(self) -> ModelInfo:
        return ModelInfo(
            name="CrySense CNN Spectrogram Classifier",
            version="1.0.0",
            classes=BABY_STATES,
            input_shape=(128, 128, 1),
            status=self.status
        )

    def fallback_prediction(self, audio_path: Path) -> PredictionResponse:
        import librosa
        try:
            raw_data, sr = librosa.load(str(audio_path), sr=22050, mono=True)
            original_rms = float(np.sqrt(np.mean(raw_data ** 2))) if raw_data.size else 0.0
            zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=raw_data))) if raw_data.size else 0.0
            centroid = float(np.mean(librosa.feature.spectral_centroid(y=raw_data, sr=sr))) if raw_data.size else 0.0
        except Exception:
            original_rms = 0.05
            zcr = 0.08
            centroid = 1800.0

        # Run heuristic directly for fallback
        dsp_baby_probs = np.zeros(5)
        if original_rms < 0.015:
            dsp_baby_probs[4] = 0.75  # Neutral
            dsp_baby_probs[2] = 0.20  # Sleepy
            dsp_baby_probs[3] = 0.05  # Discomfort
        elif original_rms > 0.12:
            if zcr > 0.12 or centroid > 2400:
                dsp_baby_probs[1] = 0.70  # Pain
                dsp_baby_probs[0] = 0.15  # Hunger
                dsp_baby_probs[3] = 0.15  # Discomfort
            else:
                dsp_baby_probs[0] = 0.60  # Hunger
                dsp_baby_probs[1] = 0.20  # Pain
                dsp_baby_probs[3] = 0.20  # Discomfort
        else:
            if zcr > 0.13 or centroid > 2100:
                dsp_baby_probs[0] = 0.50  # Hunger
                dsp_baby_probs[3] = 0.30  # Discomfort
                dsp_baby_probs[1] = 0.20  # Pain
            elif zcr > 0.075:
                dsp_baby_probs[3] = 0.50  # Discomfort
                dsp_baby_probs[2] = 0.30  # Sleepy
                dsp_baby_probs[4] = 0.20  # Neutral
            else:
                dsp_baby_probs[2] = 0.60  # Sleepy
                dsp_baby_probs[4] = 0.30  # Neutral
                dsp_baby_probs[3] = 0.10  # Discomfort

        class_index = int(np.argmax(dsp_baby_probs))
        confidence = float(dsp_baby_probs[class_index] * 100)
        baby_state = BABY_STATES[class_index]

        # Calculate distress score
        distress = self._distress_score(baby_state, confidence, dsp_baby_probs)
        scaled_distress = min(100.0, max(5.0, distress * 0.4 + (original_rms * 250.0) + (zcr * 200.0)))
        risk = self._risk_category(scaled_distress)

        distribution = {
            BABY_STATES[i]: round(float(dsp_baby_probs[i]) * 100, 2)
            for i in range(len(BABY_STATES))
        }

        summary = f"Baby states fallback prediction active (model not loaded). Acoustic energy ({original_rms:.3f}) suggests child is '{baby_state.lower()}' ({risk.lower()} risk)."

        return PredictionResponse(
            distress_score=round(scaled_distress, 2),
            confidence_score=round(confidence, 2),
            emotion=baby_state,
            risk_category=risk,
            summary=summary,
            emotion_distribution=distribution
        )

    def _distress_score(self, emotion: str, confidence: float, probabilities) -> float:
        weights = {
            "Pain": 1.0,
            "Hunger": 0.75,
            "Discomfort": 0.50,
            "Sleepy": 0.20,
            "Neutral": 0.05
        }
        weighted = sum(float(probabilities[index]) * weights.get(label, 0.2) for index, label in enumerate(BABY_STATES))
        return min(100.0, max(confidence * weights.get(emotion, 0.2), weighted * 100))

    def _risk_category(self, score: float) -> str:
        if score >= 80:
            return "High"
        if score >= 65:
            return "Elevated"
        if score >= 40:
            return "Moderate"
        return "Low"
