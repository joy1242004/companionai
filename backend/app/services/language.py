from __future__ import annotations

from collections import Counter
from typing import Iterable

COMMON_LANGUAGE_MARKERS = {
    "en": {"the", "you", "is", "friend", "hello"},
    "es": {"hola", "gracias", "amigo", "estoy", "buen"},
    "fr": {"bonjour", "merci", "ami", "bien", "suis"},
    "hi": {"namaste", "dhanyavad", "dost", "kaise", "hain"},
}


def detect_language(text: str) -> str:
    lowered = text.lower()
    scores = Counter({lang: 0 for lang in COMMON_LANGUAGE_MARKERS})
    for lang, markers in COMMON_LANGUAGE_MARKERS.items():
        for marker in markers:
            if marker in lowered:
                scores[lang] += 1
    if any(scores.values()):
        return scores.most_common(1)[0][0]
    if any(ch in lowered for ch in {"¿", "¡", "ñ"}):
        return "es"
    if any(ch in lowered for ch in {"é", "è", "ç", "à"}):
        return "fr"
    if any(ord(ch) > 127 for ch in lowered):
        return "hi"
    return "en"


def format_reply(language: str, message: str, sentiment: str) -> str:
    templates: dict[str, str] = {
        "en": "I hear you. {sentiment_line} You said: '{message}'.",
        "es": "Te escucho. {sentiment_line} Dijiste: '{message}'.",
        "fr": "Je t'écoute. {sentiment_line} Tu as dit : '{message}'.",
        "hi": "मैं सुन रहा हूँ। {sentiment_line} आपने कहा: '{message}'.",
    }
    sentiment_lines = {
        "positive": {
            "en": "That sounds uplifting!",
            "es": "¡Eso suena alentador!",
            "fr": "Cela semble encourageant !",
            "hi": "यह बहुत अच्छा लग रहा है!",
        },
        "negative": {
            "en": "I'm sorry you're feeling this way.",
            "es": "Siento que te sientas así.",
            "fr": "Je suis désolé que tu te sentes ainsi.",
            "hi": "मुझे अफ़सोस है कि आप ऐसा महसूस कर रहे हैं।",
        },
        "neutral": {
            "en": "Thanks for sharing with me.",
            "es": "Gracias por compartir conmigo.",
            "fr": "Merci de partager avec moi.",
            "hi": "मुझसे साझा करने के लिए धन्यवाद।",
        },
    }

    template = templates.get(language, templates["en"])
    sentiment_line = sentiment_lines.get(sentiment, sentiment_lines["neutral"]).get(language, sentiment_lines["neutral"]["en"])
    return template.format(sentiment_line=sentiment_line, message=message)
