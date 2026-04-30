from pydantic import BaseModel
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    USER = 'user'
    ADMIN = 'admin'


class UserCreate(BaseModel):
    email: str
    password: str
    role: UserRole = UserRole.USER

class UserOut(BaseModel):
    id: int
    email: str
    role: UserRole

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None