from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..schemas.user import UserPublic, UserUpdateSettings
from .deps import get_current_user, get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def read_profile(current_user: User = Depends(get_current_user)) -> UserPublic:
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_profile(
    payload: UserUpdateSettings,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    if payload.history_enabled is not None:
        current_user.history_enabled = payload.history_enabled
    if payload.display_name is not None:
        current_user.display_name = payload.display_name
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
