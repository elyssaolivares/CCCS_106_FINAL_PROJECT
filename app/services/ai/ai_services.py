"""
AI Categorisation Service – v2
================================
Pipeline:
  1. Text preprocessing  – lowercase, strip punctuation, remove stopwords
  2. Feature extraction   – TF-IDF (uni + bigrams)
  3. Primary classifier   – ComplementNB  (good for small / imbalanced data)
  4. Confidence gate      – if P(best) < threshold → fall back to kNN on
                            TF-IDF embeddings (semantic search)
  5. Unknown logging      – low-confidence predictions are logged so the
                            dataset can be expanded for retraining
  6. Offline retraining   – `retrain_and_save()` trains, evaluates, and
                            persists a versioned model to disk; the live
                            service hot-loads the latest version on startup.

Public API (unchanged):
    predict_category(text, return_confidence=False)
    is_gibberish(text)
"""

from __future__ import annotations

import csv
import datetime
import json
import os
import re
import string
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score

# ─── paths ───────────────────────────────────────────────────────────────────
_DIR        = Path(__file__).resolve().parent
_DATASET    = _DIR / "dataset.csv"
_MODEL_DIR  = _DIR / "models"
_LOG_DIR    = Path(__file__).resolve().parents[3] / "storage" / "data"

# ─── constants ───────────────────────────────────────────────────────────────
_CONFIDENCE_THRESHOLD = 0.40        # below this → kNN fallback
_KNN_CONFIDENCE_THRESHOLD = 0.30    # below this → "Uncategorized"
_KNN_K = 3

# Label normalisation map (merge near-duplicates in the CSV)
_LABEL_REMAP: Dict[str, str] = {
    "Furniture": "Classroom & Furniture",
}

# ─── English stop-words (minimal, avoids NLTK dependency) ────────────────────
_STOP_WORDS = frozenset(
    "a an the is are was were be been being have has had do does did will would "
    "shall should may might can could am i me my we our you your he she it they "
    "them his her its their this that these those at by for from in of on to and "
    "but or nor not so yet very too also just about above after again all any "
    "because before between both each few more most no other over same some such "
    "than then there up out with into through during".split()
)

# ─── synonym augmentation templates ──────────────────────────────────────────
_AUGMENTATION_MAP: Dict[str, List[str]] = {
    "Classroom & Furniture": [
        "wobbly chair in classroom", "desk is falling apart", "broken armrest on chair",
        "table has loose screws", "cracked desk surface", "chair leg snapped",
        "bent chair frame", "missing desk drawer", "unstable lecture table",
        "seat cushion torn", "chair wheel broken", "foldable chair won't fold",
        "desk too wobbly to write on", "armchair cushion ripped",
    ],
    "Building & Facilities": [
        "ceiling leaking water", "crack on the wall", "elevator not working",
        "emergency exit blocked", "broken glass on door", "paint peeling off wall",
        "damaged ceiling tiles", "hallway light out", "roof has a hole",
        "water stain on ceiling", "wall outlet sparking", "staircase railing loose",
        "exit sign not lit", "fire extinguisher expired", "broken door lock",
        "window won't close", "building smells like gas",
        "cracked wall in building", "wall is cracking", "concrete wall damaged",
        "broken floor tiles", "ceiling fan not working", "elevator stuck on floor",
        "escalator broken", "parking lot light out", "gate won't open",
    ],
    "Plumbing": [
        "water dripping from faucet", "toilet won't flush", "bathroom flooding",
        "sink is overflowing", "water heater broken", "rusty pipes visible",
        "water pressure too low", "urinal leaking", "shower drain clogged",
        "hot water not working in bathroom", "pipe burst in ceiling",
        "faucet handle broken", "sewage smell in restroom",
    ],
    "ICT & Equipment": [
        "projector bulb burned out", "laptop won't turn on", "screen is cracked",
        "wifi keeps disconnecting", "bluetooth not working", "USB port broken",
        "network cable damaged", "HDMI port not detected", "speaker has no sound",
        "webcam not working", "smartboard unresponsive", "software keeps crashing",
        "access point offline", "server room too hot", "mouse scroll broken",
        "monitor flickering", "keyboard keys stuck",
    ],
    "Cleaning & Sanitation": [
        "hallway smells bad", "trash not collected", "bathroom needs cleaning",
        "vomit on floor", "muddy footprints everywhere", "cobwebs in corners",
        "restroom out of soap", "no paper towels", "hand dryer broken",
        "sanitizer dispenser empty", "food waste on desk", "insects in classroom",
        "bird droppings on window sill", "wet floor not marked",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
#  Text preprocessing
# ═══════════════════════════════════════════════════════════════════════════════

def _preprocess(text: str) -> str:
    """Lowercase → strip punctuation → remove stop-words → collapse spaces."""
    text = (text or "").lower().strip()
    # Remove punctuation (keep spaces)
    text = text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))
    # Remove digits
    text = re.sub(r"\d+", " ", text)
    # Remove stop-words
    tokens = [w for w in text.split() if w not in _STOP_WORDS and len(w) > 1]
    return " ".join(tokens)


def is_gibberish(text: str) -> bool:
    """Return True if *text* is empty or likely not a meaningful sentence."""
    text = text.strip()
    if not text:
        return True
    words = re.findall(r"[a-zA-Z]+", text)
    if len(words) == 0:
        return True
    if len(words) == 1 and len(words[0]) <= 2:
        return True
    return False


# ═══════════════════════════════════════════════════════════════════════════════
#  Data loading + augmentation
# ═══════════════════════════════════════════════════════════════════════════════

def _load_dataset() -> Tuple[List[str], List[str]]:
    """Load CSV + merge augmentation. Returns (texts, labels)."""
    if not _DATASET.exists():
        print(f"[AI] Dataset not found at {_DATASET}")
        return [], []

    df = pd.read_csv(_DATASET)
    df["text"]  = df["text"].astype(str)
    df["label"] = df["label"].map(lambda l: _LABEL_REMAP.get(l, l))

    # Append augmentation rows
    aug_rows: List[dict] = []
    for label, phrases in _AUGMENTATION_MAP.items():
        for p in phrases:
            aug_rows.append({"text": p, "label": label})
    if aug_rows:
        df = pd.concat([df, pd.DataFrame(aug_rows)], ignore_index=True)

    texts  = df["text"].tolist()
    labels = df["label"].tolist()
    return texts, labels


# ═══════════════════════════════════════════════════════════════════════════════
#  Model wrapper
# ═══════════════════════════════════════════════════════════════════════════════

class _AIModel:
    """Encapsulates the full categorisation pipeline."""

    def __init__(self):
        self.tfidf: Optional[TfidfVectorizer] = None
        self.primary_clf = None               # ComplementNB
        self.fallback_clf = None              # kNN
        self.classes: Optional[np.ndarray] = None
        self.version: str = "0"
        self._ready = False

    # ── training ──────────────────────────────────────────────────────────
    def train(self, texts: List[str], labels: List[str]) -> dict:
        """Train TF-IDF + ComplementNB (primary) + kNN (fallback)."""
        processed = [_preprocess(t) for t in texts]

        # TF-IDF with unigrams + bigrams
        self.tfidf = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=3000,
            sublinear_tf=True,
            min_df=1,
        )
        X = self.tfidf.fit_transform(processed)

        # Primary: ComplementNB (handles imbalance better than MultinomialNB)
        # Fit with string labels directly so classes_ stays as strings
        self.primary_clf = ComplementNB(alpha=0.3)
        self.primary_clf.fit(X, labels)
        self.classes = self.primary_clf.classes_

        # Cross-val score for reporting
        cv = min(5, len(set(labels)))
        nb_scores = cross_val_score(self.primary_clf, X, labels, cv=cv, scoring="accuracy")

        # Fallback: kNN on TF-IDF vectors (acts as "semantic search")
        self.fallback_clf = KNeighborsClassifier(
            n_neighbors=min(_KNN_K, len(texts) - 1),
            metric="cosine",
            weights="distance",
        )
        self.fallback_clf.fit(X, labels)
        knn_scores = cross_val_score(self.fallback_clf, X, labels, cv=cv, scoring="accuracy")

        self._ready = True
        self.version = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        return {
            "version": self.version,
            "samples": len(texts),
            "classes": list(self.classes),
            "nb_cv_accuracy": round(float(nb_scores.mean()), 4),
            "knn_cv_accuracy": round(float(knn_scores.mean()), 4),
        }

    # ── prediction ────────────────────────────────────────────────────────
    def predict(self, text: str) -> Tuple[str, float]:
        """Return (category, confidence).  Falls back to kNN when NB is unsure."""
        if not self._ready:
            return ("Uncategorized", 0.0)

        processed = _preprocess(text)
        if not processed:
            return ("Uncategorized", 0.0)

        X = self.tfidf.transform([processed])
        if X.nnz == 0:
            return ("Uncategorized", 0.0)

        # --- primary: ComplementNB ---
        probs = self.primary_clf.predict_proba(X)[0]
        best_idx = int(probs.argmax())
        best_conf = float(probs[best_idx])
        category = self.classes[best_idx]

        if best_conf >= _CONFIDENCE_THRESHOLD:
            return (category, best_conf)

        # --- fallback: kNN (semantic search via TF-IDF cosine) ---
        knn_probs = self.fallback_clf.predict_proba(X)[0]
        knn_idx = int(knn_probs.argmax())
        knn_conf = float(knn_probs[knn_idx])
        knn_cat = self.classes[knn_idx]

        if knn_conf >= _KNN_CONFIDENCE_THRESHOLD:
            return (knn_cat, knn_conf)

        # Both classifiers are unsure
        return ("Uncategorized", max(best_conf, knn_conf))

    # ── persistence ───────────────────────────────────────────────────────
    def save(self, directory: Optional[Path] = None):
        """Save model artefacts to *directory* (defaults to models/)."""
        d = directory or _MODEL_DIR
        d.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.tfidf, d / "tfidf.pkl")
        joblib.dump(self.primary_clf, d / "primary_clf.pkl")
        joblib.dump(self.fallback_clf, d / "fallback_clf.pkl")
        meta = {
            "version": self.version,
            "classes": list(self.classes) if self.classes is not None else [],
            "threshold": _CONFIDENCE_THRESHOLD,
            "knn_threshold": _KNN_CONFIDENCE_THRESHOLD,
        }
        (d / "meta.json").write_text(json.dumps(meta, indent=2))
        print(f"[AI] Model v{self.version} saved to {d}")

    def load(self, directory: Optional[Path] = None) -> bool:
        """Load model artefacts.  Returns True on success."""
        d = directory or _MODEL_DIR
        try:
            self.tfidf        = joblib.load(d / "tfidf.pkl")
            self.primary_clf  = joblib.load(d / "primary_clf.pkl")
            self.fallback_clf = joblib.load(d / "fallback_clf.pkl")
            self.classes = self.primary_clf.classes_
            meta = json.loads((d / "meta.json").read_text())
            self.version = meta.get("version", "loaded")
            self._ready = True
            print(f"[AI] Loaded model v{self.version} from {d}")
            return True
        except Exception as exc:
            print(f"[AI] Could not load model from {d}: {exc}")
            return False


# ═══════════════════════════════════════════════════════════════════════════════
#  Unknown-input logger
# ═══════════════════════════════════════════════════════════════════════════════

def _log_unknown(text: str, predicted: str, confidence: float):
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = _LOG_DIR / "unknown_predictions.csv"
    file_exists = log_file.exists()
    try:
        with open(log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "text", "predicted", "confidence"])
            writer.writerow([
                datetime.datetime.now().isoformat(),
                text,
                predicted,
                f"{confidence:.4f}",
            ])
    except Exception as exc:
        print(f"[AI] Failed to log unknown prediction: {exc}")


# ═══════════════════════════════════════════════════════════════════════════════
#  Module-level singleton + startup
# ═══════════════════════════════════════════════════════════════════════════════

_model = _AIModel()


def _startup():
    """Try to load a saved model; if missing, train from CSV and save."""
    if _model.load():
        return
    texts, labels = _load_dataset()
    if not texts:
        print("[AI] No training data — model will return 'Uncategorized'.")
        return
    info = _model.train(texts, labels)
    print(f"[AI] Trained fresh model: {info}")
    _model.save()

_startup()

vectorizer = _model.tfidf
model = _model.primary_clf


# ═══════════════════════════════════════════════════════════════════════════════
#  Public API  (backward-compatible)
# ═══════════════════════════════════════════════════════════════════════════════

def predict_category(text: str, return_confidence: bool = False):
    """Predict the report category for *text*.

    Returns:
        str             – category name  (when return_confidence is False)
        (str, float)    – (category, confidence)  (when return_confidence is True)
    """
    text_norm = (text or "").strip()
    if is_gibberish(text_norm):
        return ("Uncategorized", 0.0) if return_confidence else "Uncategorized"

    category, confidence = _model.predict(text_norm)

    # Log low-confidence or "Uncategorized" for later review
    if confidence < _CONFIDENCE_THRESHOLD or category == "Uncategorized":
        _log_unknown(text_norm, category, confidence)

    return (category, confidence) if return_confidence else category


# ─── Retraining entry-point  (call offline or from admin panel) ──────────────

def retrain_and_save() -> dict:
    """Reload CSV + augmentation, retrain, save versioned model. Returns info dict."""
    texts, labels = _load_dataset()
    if not texts:
        return {"error": "No training data found"}
    info = _model.train(texts, labels)
    _model.save()
    return info


def load_and_train_model():
    """Legacy shim kept for backward-compatibility with tests."""
    global vectorizer, model
    retrain_and_save()
    vectorizer = _model.tfidf
    model = _model.primary_clf

