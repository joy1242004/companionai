from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = None
    include_facial_mood: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    language: str
    sentiment: str
    mood: str
    timestamp: datetime


class ChatMessagePublic(BaseModel):
    id: int
    sender: str
    language: str
    sentiment: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True
