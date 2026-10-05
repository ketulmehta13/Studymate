
"""
Predictor service for academic topic classification.
Uses trained TF-IDF and Logistic Regression models.
"""
import os
import sys
import pickle
from pathlib import Path
from typing import Dict, Any, Optional

# Add backend directory to sys.path for direct script execution
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.logging_config import get_logger

logger = get_logger("classifier.predictor")

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
VEC_PATH = MODELS_DIR / "vectorizer.pkl"
CLF_PATH = MODELS_DIR / "classifier.pkl"

_vectorizer = None
_classifier = None
CONFIDENCE_THRESHOLD = 0.25


def _ensure_models_loaded() -> None:
    """Lazy-loads models; automatically trains them if not yet present."""
    global _vectorizer, _classifier
    if _vectorizer is not None and _classifier is not None:
        return

    if not VEC_PATH.exists() or not CLF_PATH.exists():
        logger.info("Classifier models not found on disk. Initiating training...")
        from ai.classifier.train import train_and_save_model
        train_and_save_model()

    with open(VEC_PATH, "rb") as f:
        _vectorizer = pickle.load(f)

    with open(CLF_PATH, "rb") as f:
        _classifier = pickle.load(f)

    logger.info("Classifier models loaded into memory successfully.")


def predict_topic(text: str) -> Dict[str, Any]:
    """
    Predicts academic topic for given text snippet.
    Returns:
        {
            "topic": "NLP",
            "confidence": 0.91
        }
    Falls back to 'Other' if confidence is below threshold or input is empty.
    """
    if not text or not text.strip() or len(text.strip()) < 10:
        return {
            "topic": "Other",
            "confidence": 0.0,
        }

    _ensure_models_loaded()

    clean_text = text.strip()
    X_tfidf = _vectorizer.transform([clean_text])
    probabilities = _classifier.predict_proba(X_tfidf)[0]
    classes = _classifier.classes_

    best_index = probabilities.argmax()
    confidence = float(probabilities[best_index])
    predicted_topic = str(classes[best_index])

    if confidence < CONFIDENCE_THRESHOLD:
        logger.info(f"Prediction confidence {confidence:.2f} below threshold {CONFIDENCE_THRESHOLD}. Defaulting to 'Other'.")
        return {
            "topic": "Other",
            "confidence": round(confidence, 2),
        }

    return {
        "topic": predicted_topic,
        "confidence": round(confidence, 2),
    }
