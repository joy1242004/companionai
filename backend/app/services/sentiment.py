from __future__ import annotations

from typing import Iterable

POSITIVE_WORDS = {"happy", "great", "fantastic", "amazing", "love", "उत्साहित", "खुश", "bien", "genial", "merci", "gracias"}
NEGATIVE_WORDS = {"sad", "tired", "angry", "bad", "hate", "alone", "triste", "mal", "désolé", "दुखी", "थका"}


def detect_sentiment(text: str) -> str:
    lowered = text.lower()
    positive_hits = sum(1 for word in POSITIVE_WORDS if word in lowered)
    negative_hits = sum(1 for word in NEGATIVE_WORDS if word in lowered)
    if positive_hits > negative_hits:
        return "positive"
    if negative_hits > positive_hits:
        return "negative"
    return "neutral"


MOOD_BY_SENTIMENT = {
    "positive": "uplifted",
    "negative": "concerned",
    "neutral": "calm",
}


def mood_from_sentiment(sentiment: str, fallback: str | None = None) -> str:
    return MOOD_BY_SENTIMENT.get(sentiment, fallback or "calm")
