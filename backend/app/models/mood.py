from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..core.database import Base


class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    mood = Column(String, nullable=False)
    source = Column(String, default="chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    mood_date = Column(Date, default=date.today, index=True)

    user = relationship("User", back_populates="mood_entries")
