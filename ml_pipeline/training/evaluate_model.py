import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

from ml_pipeline.preprocessing.feature_extraction import audio_file_to_spectrogram


def evaluate(model_path: str, manifest_path: str):
    model = tf.keras.models.load_model(model_path)
    manifest = pd.read_csv(manifest_path)
    x = np.stack([audio_file_to_spectrogram(path) for path in manifest["path"]])
    y_true = manifest["label"].to_list()
    labels = Path(model_path).with_suffix(".labels.txt").read_text(encoding="utf-8").splitlines()
    y_pred_indices = np.argmax(model.predict(x), axis=1)
    y_pred = [labels[index] for index in y_pred_indices]
    return {
        "classification_report": classification_report(y_true, y_pred, output_dict=True),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist()
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    print(evaluate(args.model, args.manifest))
