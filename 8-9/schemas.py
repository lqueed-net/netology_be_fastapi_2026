from pydantic import BaseModel
from typing import Optional

# Определение ролей для Pydantic моделей
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserCreate(BaseModel):
    email: str
    password: str
    # При создании пользователя роль по умолчанию - обычный пользователь
    role: UserRole = UserRole.USER

class UserOut(BaseModel):
    id: int
    email: str
    role: UserRole

    class Config:
        from_attributes = True  # для совместимости с SQLAlchemy (в Pydantic v2)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserUpdate(BaseModel):
    # Поля для обновления профиля пользователя
    email: Optional[str] = None
    password: Optional[str] = None