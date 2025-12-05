import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from typing import List
import re
import os


vectorizer = None
model = None

# load dataset and train the model once on import
def load_and_train_model():
    global vectorizer, model

    dataset_path = os.path.join(os.path.dirname(__file__), "dataset.csv")
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset not found at: {dataset_path}")
        return

    # load CSV and clean text
    df = pd.read_csv(dataset_path)
    df["text"] = df["text"].astype(str).str.lower().str.strip()

    texts: List[str] = df["text"].tolist()
    labels: List[str] = df["label"].tolist()

    # convert text to numerical features
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(texts)

    # train Multinomial Naive Bayes classifier
    model = MultinomialNB()
    model.fit(X, labels)

# train model immediately
load_and_train_model()

# helper: Detect gibberish or empty input
def is_gibberish(text: str) -> bool:
    text = text.strip()
    if not text:
        return True
    words = re.findall(r"[a-zA-Z]+", text)
    if len(words) == 0:
        return True
    # single very short word is considered gibberish
    if len(words) == 1 and len(words[0]) <= 2:
        return True
    return False

# predict category for a given text
def predict_category(text: str, return_confidence: bool = False):
    global vectorizer, model

    # if model not loaded, return Uncategorized
    if vectorizer is None or model is None:
        return ("Uncategorized", 0.0) if return_confidence else "Uncategorized"

    text_norm = (text or "").lower().strip()

    # check for gibberish or empty input
    if is_gibberish(text_norm):
        return ("Uncategorized", 0.0) if return_confidence else "Uncategorized"

    # check if any words are known to the model
    tokens = re.findall(r"[a-zA-Z]+", text_norm)
    known_tokens = sum(1 for t in tokens if t in vectorizer.vocabulary_)
    if known_tokens == 0:
        return ("Uncategorized", 0.0) if return_confidence else "Uncategorized"

    # transform text to vector and predict probabilities
    X_new = vectorizer.transform([text_norm])
    if X_new.nnz == 0:
        return ("Uncategorized", 0.0) if return_confidence else "Uncategorized"

    probs = model.predict_proba(X_new)[0]
    max_idx = probs.argmax()
    category = model.classes_[max_idx]


    return (category) if return_confidence else category
