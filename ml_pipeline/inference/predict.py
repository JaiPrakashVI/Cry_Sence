from pathlib import Path

import numpy as np
import tensorflow as tf

from ml_pipeline.preprocessing.feature_extraction import audio_file_to_spectrogram

DEFAULT_LABELS = ["Distress", "Crying", "Fear", "Panic", "Sadness", "Neutral", "Happy", "Angry"]


def load_labels(model_path: str) -> list[str]:
    label_path = Path(model_path).with_suffix(".labels.txt")
    if label_path.exists():
        return label_path.read_text(encoding="utf-8").splitlines()
    return DEFAULT_LABELS


def load_model(model_path: str) -> tf.keras.Model:
    return tf.keras.models.load_model(model_path)


def predict_audio_file(audio_path: str, model=None, model_path: str | None = None) -> dict:
    if model is None:
        if model_path is None:
            raise ValueError("Either model or model_path must be provided.")
        model = load_model(model_path)

    labels = load_labels(model_path or "")
    spectrogram = audio_file_to_spectrogram(audio_path)
    probabilities = model.predict(np.expand_dims(spectrogram, axis=0), verbose=0)[0]
    class_index = int(np.argmax(probabilities))
    confidence = float(probabilities[class_index] * 100)
    emotion = labels[class_index] if class_index < len(labels) else DEFAULT_LABELS[class_index]
    distress_score = calculate_distress_score(emotion, confidence, probabilities, labels)

    return {
        "distress_score": round(distress_score, 2),
        "confidence_score": round(confidence, 2),
        "emotion": emotion,
        "risk_category": risk_category(distress_score),
        "summary": f"Detected {emotion.lower()} with {confidence:.1f}% confidence using CNN spectrogram inference."
    }


def calculate_distress_score(emotion: str, confidence: float, probabilities, labels: list[str]) -> float:
    weights = {
        "Distress": 1.0,
        "Panic": 0.95,
        "Fear": 0.82,
        "Crying": 0.74,
        "Sadness": 0.56,
        "Angry": 0.5,
        "Neutral": 0.12,
        "Happy": 0.05
    }
    weighted = sum(float(probabilities[index]) * weights.get(label, 0.2) for index, label in enumerate(labels))
    return min(100.0, max(confidence * weights.get(emotion, 0.2), weighted * 100))


def risk_category(score: float) -> str:
    if score >= 80:
        return "High"
    if score >= 65:
        return "Elevated"
    if score >= 40:
        return "Moderate"
    return "Low"
