import sys
from pathlib import Path
import numpy as np
import soundfile as sf

# Set PYTHONPATH to root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.services.prediction_service import PredictionService
from backend.app.services.inference_service import InferenceService
from backend.app.utils.config import get_settings
from backend.app.models.audio import AudioMetadata

def test_predictions():
    settings = get_settings()
    inference_service = InferenceService(settings.model_path)
    prediction_service = PredictionService(inference_service)

    # Create temp directory
    temp_dir = Path("backend/storage/temp_test")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    sr = 22050
    duration = 3
    t = np.linspace(0, duration, sr * duration, endpoint=False)
    
    # 1. Quiet signal (should yield low distress, sleepy/neutral)
    quiet_signal = 0.002 * np.sin(2 * np.pi * 300 * t)
    quiet_file = temp_dir / "quiet.wav"
    sf.write(str(quiet_file), quiet_signal, sr, format="WAV", subtype="PCM_16")
    
    # 2. Loud/high frequency signal (should yield high distress, pain)
    loud_signal = 0.8 * np.sin(2 * np.pi * 1200 * t)
    # Add some high-freq noise to increase zero-crossing rate and spectral centroid
    loud_signal += 0.1 * np.random.normal(0, 1, len(t))
    # Normalize to keep within bounds
    loud_signal = loud_signal / np.max(np.abs(loud_signal))
    loud_file = temp_dir / "loud.wav"
    sf.write(str(loud_file), loud_signal, sr, format="WAV", subtype="PCM_16")
    
    print("----- PREDICTING QUIET AUDIO -----")
    meta1 = AudioMetadata(
        path=quiet_file,
        original_filename="quiet.wav",
        content_type="audio/wav",
        size_bytes=quiet_file.stat().st_size,
        duration_seconds=duration,
        sample_rate=sr,
        channels=1
    )
    res1 = prediction_service.analyze(meta1, "trace_quiet")
    print(f"Result 1: PrimaryState={res1.emotion}, Distress={res1.distress_score}, Confidence={res1.confidence_score}, Risk={res1.risk_category}")
    print(f"Distribution: {res1.emotion_distribution}")
    print(f"Summary: {res1.summary}\n")
    
    print("----- PREDICTING LOUD AUDIO -----")
    meta2 = AudioMetadata(
        path=loud_file,
        original_filename="loud.wav",
        content_type="audio/wav",
        size_bytes=loud_file.stat().st_size,
        duration_seconds=duration,
        sample_rate=sr,
        channels=1
    )
    res2 = prediction_service.analyze(meta2, "trace_loud")
    print(f"Result 2: PrimaryState={res2.emotion}, Distress={res2.distress_score}, Confidence={res2.confidence_score}, Risk={res2.risk_category}")
    print(f"Distribution: {res2.emotion_distribution}")
    print(f"Summary: {res2.summary}\n")

    # Clean up
    quiet_file.unlink(missing_ok=True)
    loud_file.unlink(missing_ok=True)
    try:
        temp_dir.rmdir()
    except Exception:
        pass

if __name__ == "__main__":
    test_predictions()
