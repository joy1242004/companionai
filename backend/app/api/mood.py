from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.mood import MoodEntry
from ..schemas.mood import MoodEntryCreate, MoodEntryPublic
from .deps import get_current_user, get_db

router = APIRouter(prefix="/mood", tags=["mood"])


@router.get("/entries", response_model=List[MoodEntryPublic])
async def list_entries(
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[MoodEntryPublic]:
    query = select(MoodEntry).where(MoodEntry.user_id == current_user.id)
    if start is not None:
        query = query.where(MoodEntry.mood_date >= start)
    if end is not None:
        query = query.where(MoodEntry.mood_date <= end)
    result = await db.execute(query.order_by(MoodEntry.mood_date.asc()))
    return result.scalars().all()


@router.post("/entries", response_model=MoodEntryPublic, status_code=status.HTTP_201_CREATED)
async def create_entry(
    payload: MoodEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> MoodEntryPublic:
    entry = MoodEntry(user_id=current_user.id, mood=payload.mood, source=payload.source, mood_date=payload.mood_date)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(entry_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> None:
    entry = await db.get(MoodEntry, entry_id)
    if entry is None or entry.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mood entry not found")
    await db.delete(entry)
    await db.commit()
