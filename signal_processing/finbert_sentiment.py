import logging
from typing import List, Dict

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError:
    TfidfVectorizer = None

try:
    from transformers import pipeline
except ImportError:
    pipeline = None


def _get_sentiment_pipeline():
    if pipeline is None:
        raise RuntimeError("Transformers package is required for FinBERT sentiment.")
    try:
        return pipeline("sentiment-analysis", model="ProsusAI/finbert")
    except Exception:
        logging.warning("FinBERT unavailable, falling back to general sentiment model.")
        return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")


def analyze_news_sentiment(news_items: List[Dict]) -> float:
    if not news_items:
        return 0.0

    try:
        sentiment_pipeline = _get_sentiment_pipeline()
    except RuntimeError:
        # Fallback simple sentiment estimation
        return 0.0

    total_score = 0.0
    count = 0

    for item in news_items:
        text = item.get("title", "") or item.get("summary", "") or ""
        if not text:
            continue
        try:
            out = sentiment_pipeline(text[:512])[0]
            label = out.get("label", "NEUTRAL").lower()
            score = out.get("score", 0.0)
            if label in ["positive", "bullish"]:
                total_score += score
            elif label in ["negative", "bearish"]:
                total_score -= score
            else:
                pass
            count += 1
        except Exception:
            continue

    if count == 0:
        return 0.0

    normalized = max(min(total_score / count, 1.0), -1.0)
    return round(normalized, 4)


def vectorize_news(news_items: List[Dict]):
    if TfidfVectorizer is None:
        logging.warning("scikit-learn not installed: vectorize_news unavailable")
        return None, None

    entries = []
    for item in news_items:
        text = item.get("title", "") + " " + item.get("summary", "")
        entries.append(text.strip())

    vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
    if len(entries) == 0 or all(not e for e in entries):
        return None, vectorizer

    matrix = vectorizer.fit_transform(entries)
    return matrix, vectorizer
