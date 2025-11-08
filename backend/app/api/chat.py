from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.chat import ChatMessage
from ..schemas.chat import ChatMessagePublic, ChatRequest, ChatResponse
from ..services.conversation import handle_chat
from .deps import get_current_user, get_db

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/respond", response_model=ChatResponse)
async def create_reply(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ChatResponse:
    return await handle_chat(session=db, user=current_user, payload=payload)


@router.get("/history", response_model=list[ChatMessagePublic])
async def get_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[ChatMessagePublic]:
    if not current_user.history_enabled:
        return []
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    messages = list(reversed(result.scalars().all()))
    return messages
