from datetime import date, datetime
from typing import List

from pydantic import BaseModel


class MoodEntryCreate(BaseModel):
    mood: str
    source: str
    mood_date: date


class MoodEntryPublic(BaseModel):
    id: int
    mood: str
    source: str
    mood_date: date
    created_at: datetime

    class Config:
        orm_mode = True


class MoodSeries(BaseModel):
    entries: List[MoodEntryPublic]
