from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr


# Pydantic's ``EmailStr`` type depends on the optional ``email_validator`` package.
# The execution environment that runs the sample app cannot install additional
# wheels from the internet, which caused the application to crash on import.  We
# replicate the essential behaviour with a light-weight constrained string that
# validates the general ``local@domain`` structure instead of relying on the
# external dependency.
EmailStr = constr(regex=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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
