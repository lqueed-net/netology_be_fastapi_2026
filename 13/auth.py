# auth.py
# Этот модуль отвечает за всю логику аутентификации:
# - хеширование и проверка паролей (passlib + bcrypt)
# - создание и проверка JWT токенов (python-jose)
# - зависимость для получения текущего пользователя по токену
import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import schemas
from database import get_db
from models import User

from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# dotenv
load_dotenv()

# conf
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# hash
pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    bcrypt__truncate_error=False,
    deprecated="auto"
)

# oauth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# hash and pass check
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

# JWT creation
def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Получение текущего пользователя
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_db)
):
    # Создаем исключение для ошибок аутентификации
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        # Декодируем JWT токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Получаем email из токена
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception

    # Ищем пользователя в базе данных
    user = await session.execute(select(User).filter(User.email == token_data.email))
    user = user.scalar_one_or_none()
    if user is None:
        # Пользователь не найден или удален
        raise credentials_exception
    return user


# check if role
async def get_current_admin(
        current_user: User = Depends(get_current_user)
):
    # Проверяем админ ли юзер
    if current_user.role.value != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not enough privileges'
        )
    return current_user

