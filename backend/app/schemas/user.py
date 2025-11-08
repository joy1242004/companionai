from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    history_enabled: bool
    created_at: datetime

    class Config:
        orm_mode = True


class UserUpdateSettings(BaseModel):
    history_enabled: Optional[bool] = None
    display_name: Optional[str] = None
