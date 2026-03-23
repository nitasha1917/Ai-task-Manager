"""
Distraction Detector CNN
========================
Dataset : FER2013 (Kaggle - free)
         kaggle.com/datasets/msambare/fer2013
         → download fer2013.csv → place at cnn/data/fer2013.csv

Classes  : angry, disgust, fear, happy, sad, surprise, neutral
Mapped to: Focused | Distracted | Tired/Burned Out

Architecture:
    Input (48x48x1)
    → Conv(32)x2 → BN → Pool → Dropout
    → Conv(64)x2 → BN → Pool → Dropout
    → Conv(128)x2 → BN → Pool → Dropout
    → Dense(256) → Dropout
    → Dense(7, softmax)
"""

import os
import sys
import numpy as np
import pandas as pd

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# ── Constants ────────────────────────────────────────────────────────────────
IMG_SIZE    = 48
NUM_CLASSES = 7
BATCH_SIZE  = 64
MODEL_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "model", "distraction_cnn.keras")
DATA_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "data", "fer2013.csv")

EMOTION_LABELS = {
    0: "Angry",
    1: "Disgust",
    2: "Fear",
    3: "Happy",
    4: "Sad",
    5: "Surprise",
    6: "Neutral"
}

STUDY_STATE_MAP = {
    "Angry":    {"state": "Distracted",      "emoji": "😤", "color": "#e17055"},
    "Disgust":  {"state": "Distracted",      "emoji": "🤢", "color": "#e17055"},
    "Fear":     {"state": "Distracted",      "emoji": "😨", "color": "#e17055"},
    "Happy":    {"state": "Focused",         "emoji": "😊", "color": "#00b894"},
    "Sad":      {"state": "Tired/Burned Out","emoji": "😢", "color": "#fdcb6e"},
    "Surprise": {"state": "Distracted",      "emoji": "😲", "color": "#e17055"},
    "Neutral":  {"state": "Focused",         "emoji": "😐", "color": "#00b894"},
}


# ── Model ────────────────────────────────────────────────────────────────────

def build_model() -> keras.Model:
    """Build CNN for 48x48 grayscale face images."""
    model = keras.Sequential([
        # Block 1 — edges and textures
        layers.Conv2D(32, (3, 3), padding='same', input_shape=(IMG_SIZE, IMG_SIZE, 1)),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Conv2D(32, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),

        # Block 2 — eyes, mouth shapes
        layers.Conv2D(64, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Conv2D(64, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),

        # Block 3 — expression patterns
        layers.Conv2D(128, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Conv2D(128, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),

        # Classifier
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(NUM_CLASSES, activation='softmax', name='output')
    ], name="DistractionCNN")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


# ── Data ─────────────────────────────────────────────────────────────────────

def load_fer2013(csv_path: str = DATA_PATH):
    """Load FER2013 CSV → (x_train, y_train), (x_test, y_test)"""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"\n❌ Dataset not found at: {csv_path}\n\n"
            "📥 Download FREE from Kaggle:\n"
            "   https://www.kaggle.com/datasets/msambare/fer2013\n\n"
            "📁 Place the file at:\n"
            f"   {csv_path}\n"
        )

    print("📦 Loading FER2013...")
    df = pd.read_csv(csv_path)

    def parse_pixels(s):
        return np.array(s.split(), dtype='float32').reshape(IMG_SIZE, IMG_SIZE, 1) / 255.0

    train_df = df[df['Usage'] == 'Training']
    test_df  = df[df['Usage'] == 'PublicTest']

    print(f"   Train: {len(train_df)} | Test: {len(test_df)}")

    x_train = np.stack(train_df['pixels'].apply(parse_pixels).values)
    y_train = train_df['emotion'].values.astype('int32')
    x_test  = np.stack(test_df['pixels'].apply(parse_pixels).values)
    y_test  = test_df['emotion'].values.astype('int32')

    return (x_train, y_train), (x_test, y_test)


# ── Training ─────────────────────────────────────────────────────────────────

def train_model(epochs: int = 30, save_path: str = MODEL_PATH):
    """Train and save the model. Returns (model, history, test_accuracy)."""
    (x_train, y_train), (x_test, y_test) = load_fer2013()

    model = build_model()
    model.summary()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    callbacks = [
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_accuracy', factor=0.5,
            patience=4, min_lr=1e-6, verbose=1
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy', patience=8,
            restore_best_weights=True, verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            save_path, monitor='val_accuracy',
            save_best_only=True, verbose=1
        )
    ]

    datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rotation_range=10,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        zoom_range=0.1
    )

    print(f"\n🚀 Training up to {epochs} epochs (early stopping on)...")
    history = model.fit(
        datagen.flow(x_train, y_train, batch_size=BATCH_SIZE),
        steps_per_epoch=len(x_train) // BATCH_SIZE,
        epochs=epochs,
        validation_data=(x_test, y_test),
        callbacks=callbacks,
        verbose=1
    )

    _, test_acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"\n✅ Test Accuracy : {test_acc * 100:.2f}%")
    print(f"✅ Saved to      : {save_path}")

    return model, history, test_acc


# ── Inference ────────────────────────────────────────────────────────────────

def load_model(model_path: str = MODEL_PATH) -> keras.Model:
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at '{model_path}'.\n"
            "Train first: python cnn/cnn_model.py"
        )
    return keras.models.load_model(model_path)


def predict_state(model: keras.Model, image: np.ndarray) -> dict:
    """
    Predict focus state from a face image array.
    Accepts (48,48), (48,48,1), or (48,48,3) — handles all cases.
    """
    img = image.astype('float32')
    if img.max() > 1.0:
        img /= 255.0

    # RGB → grayscale
    if img.ndim == 3 and img.shape[2] == 3:
        img = np.mean(img, axis=2)
    if img.ndim == 3 and img.shape[2] == 1:
        img = img[:, :, 0]

    # Resize if needed
    if img.shape != (IMG_SIZE, IMG_SIZE):
        from PIL import Image as PILImage
        pil = PILImage.fromarray((img * 255).astype('uint8'))
        pil = pil.resize((IMG_SIZE, IMG_SIZE), PILImage.LANCZOS)
        img = np.array(pil).astype('float32') / 255.0

    inp   = img[np.newaxis, ..., np.newaxis]   # (1, 48, 48, 1)
    probs = model.predict(inp, verbose=0)[0]

    emotion_idx  = int(np.argmax(probs))
    emotion_name = EMOTION_LABELS[emotion_idx]
    study_info   = STUDY_STATE_MAP[emotion_name]

    return {
        'emotion':           emotion_name,
        'study_state':       study_info['state'],
        'emoji':             study_info['emoji'],
        'color':             study_info['color'],
        'confidence':        float(probs[emotion_idx]),
        'all_probabilities': {EMOTION_LABELS[i]: float(probs[i]) for i in range(NUM_CLASSES)}
    }


def get_fallback_advice(study_state: str) -> str:
    import random
    advice = {
        "Focused": [
            "Great focus! You're in the zone — keep it up.",
            "Excellent concentration. Consider a 5-min break after 25 minutes.",
            "You're fully engaged. This is your peak study time."
        ],
        "Distracted": [
            "You seem distracted. Try closing unnecessary tabs.",
            "Refocus: write down what's on your mind, then return.",
            "Pomodoro tip: 25 min focused, 5 min break. Reset now?"
        ],
        "Tired/Burned Out": [
            "You look tired. A 10-min break can restore focus significantly.",
            "Consider a short walk or some water before continuing.",
            "Fatigue detected — try lighter review material or a power nap."
        ]
    }
    return random.choice(advice.get(study_state, advice["Focused"]))


if __name__ == "__main__":
    epochs = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    train_model(epochs=epochs)