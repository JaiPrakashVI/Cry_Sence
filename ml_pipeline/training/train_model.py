import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from ml_pipeline.preprocessing.feature_extraction import audio_file_to_spectrogram

EMOTION_CLASSES = ["Distress", "Crying", "Fear", "Panic", "Sadness", "Neutral", "Happy", "Angry"]


def build_cnn_model(input_shape=(128, 128, 1), num_classes=len(EMOTION_CLASSES)) -> tf.keras.Model:
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=input_shape),
        tf.keras.layers.Conv2D(32, 3, activation="relu", padding="same"),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, 3, activation="relu", padding="same"),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(128, 3, activation="relu", padding="same"),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dropout(0.35),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Dense(num_classes, activation="softmax")
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def load_dataset(manifest_path: str):
    manifest = pd.read_csv(manifest_path)
    features = np.stack([audio_file_to_spectrogram(path) for path in manifest["path"]])
    encoder = LabelEncoder()
    labels = encoder.fit_transform(manifest["label"])
    return features, labels, encoder


def train(manifest_path: str, output_path: str, epochs: int = 25, batch_size: int = 16):
    x, y, encoder = load_dataset(manifest_path)
    x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2, stratify=y, random_state=42)
    model = build_cnn_model(num_classes=len(encoder.classes_))

    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=6, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(patience=3, factor=0.3),
        tf.keras.callbacks.ModelCheckpoint(output_path, save_best_only=True)
    ]

    history = model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks
    )
    Path(output_path).with_suffix(".labels.txt").write_text("\n".join(encoder.classes_), encoding="utf-8")
    return history


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="CSV with path,label columns.")
    parser.add_argument("--output", default="ml_pipeline/saved_models/crysense_cnn.keras")
    parser.add_argument("--epochs", type=int, default=25)
    args = parser.parse_args()
    train(args.manifest, args.output, epochs=args.epochs)
