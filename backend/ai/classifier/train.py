"""
Classical ML Classifier Training Script for StudyMate AI.

This module trains a TF-IDF Vectorizer and LogisticRegression classifier
to categorize academic text into:
- Machine Learning
- NLP
- Mathematics
- Deep Learning
- LLM

NOTE: The dataset provided in dataset.csv is a starter dataset.
Adding more domain-specific training examples significantly improves
accuracy and generalizes to broader academic curricula.
"""
import os
import sys
import csv
import pickle
from pathlib import Path

# Add backend directory to sys.path for direct script execution
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

from core.logging_config import get_logger

logger = get_logger("classifier.train")

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset.csv"
MODELS_DIR = BASE_DIR / "models"


def train_and_save_model(dataset_path: Path = DATASET_PATH, models_dir: Path = MODELS_DIR) -> None:
    """
    Trains TF-IDF vectorizer + LogisticRegression model on dataset.csv
    and serializes models into vectorizer.pkl and classifier.pkl.
    """
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    models_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading training dataset from {dataset_path}...")
    X, y = [], []
    with open(dataset_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "text" in row and "topic" in row:
                X.append(row["text"].strip())
                y.append(row["topic"].strip())

    if not X:
        raise ValueError("Dataset CSV contains no valid data.")

    logger.info(f"Training on {len(X)} samples across classes: {sorted(set(y))}")

    # Vectorizer with sublinear tf and n-grams
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=2500,
        sublinear_tf=True,
        stop_words="english",
    )
    X_tfidf = vectorizer.fit_transform(X)

    # Train LogisticRegression with balanced class weights
    classifier = LogisticRegression(
        C=2.0,
        max_iter=500,
        class_weight="balanced",
        random_state=42,
    )
    classifier.fit(X_tfidf, y)

    y_pred = classifier.predict(X_tfidf)
    report = classification_report(y, y_pred, zero_division=0)
    logger.info(f"Training Performance:\n{report}")

    # Save vectorizer and classifier
    vec_path = models_dir / "vectorizer.pkl"
    clf_path = models_dir / "classifier.pkl"

    with open(vec_path, "wb") as f:
        pickle.dump(vectorizer, f)

    with open(clf_path, "wb") as f:
        pickle.dump(classifier, f)

    logger.info(f"Model artifacts successfully saved to {models_dir}")


if __name__ == "__main__":
    train_and_save_model()
