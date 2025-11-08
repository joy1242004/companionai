from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.chat import ChatMessage
from ..models.mood import MoodEntry
from ..models.user import User
from ..schemas.chat import ChatRequest, ChatResponse
from ..services.language import detect_language, format_reply
from ..services.sentiment import detect_sentiment, mood_from_sentiment


async def handle_chat(
    *,
    session: AsyncSession,
    user: User,
    payload: ChatRequest,
) -> ChatResponse:
    language = payload.language or detect_language(payload.message)
    sentiment = detect_sentiment(payload.message)
    facial_mood = payload.include_facial_mood or ""
    mood = facial_mood or mood_from_sentiment(sentiment)
    reply_text = format_reply(language, payload.message, sentiment)

    timestamp = datetime.utcnow()

    if user.history_enabled:
        user_message = ChatMessage(
            user_id=user.id,
            sender="user",
            language=language,
            sentiment=sentiment,
            content=payload.message,
            created_at=timestamp,
        )
        ai_message = ChatMessage(
            user_id=user.id,
            sender="ai",
            language=language,
            sentiment=sentiment,
            content=reply_text,
            created_at=timestamp,
        )
        session.add_all([user_message, ai_message])
        mood_entry = MoodEntry(user_id=user.id, mood=mood, source="chat", mood_date=timestamp.date())
        session.add(mood_entry)
        await session.commit()

    return ChatResponse(reply=reply_text, language=language, sentiment=sentiment, mood=mood, timestamp=timestamp)
