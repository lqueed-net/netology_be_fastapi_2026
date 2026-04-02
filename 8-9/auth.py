# auth.py
# Этот модуль отвечает за всю логику аутентификации:
# - хеширование и проверка паролей (passlib + bcrypt)
# - создание и проверка JWT токенов (python-jose)
# - зависимость для получения текущего пользователя по токену
import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import schemas
from database import get_db
from models import User

from jose import JWTError, jwt
# JWTError - исключение, которое выбрасывается при проблемах с JWT (невалидная подпись, истекший срок и т.д.)
# jwt - модуль для работы с JSON Web Tokens (кодирование, декодирование)

from passlib.context import CryptContext
# CryptContext - класс из библиотеки passlib, который позволяет настроить схему хеширования паролей.
# Мы используем bcrypt с автоматической генерацией соли.

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# OAuth2PasswordBearer - класс, который создаёт зависимость для извлечения токена из заголовка Authorization.
# Он ожидает, что токен будет передан в формате Bearer <token>.
# При отсутствии или неверном формате заголовка автоматически вернёт ошибку 401.



load_dotenv()

# Конфигурация (в реальном проекте берите из переменных окружения)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Настройка контекста для хеширования паролей ---
# Схема "bcrypt" означает, что пароли будут хешироваться с помощью bcrypt.
# deprecated="auto" автоматически обрабатывает устаревшие схемы (если они были).
pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    bcrypt__truncate_error=False,  # Allow automatic truncation
    deprecated="auto"
)

# --- Создание зависимости OAuth2 ---
# tokenUrl="/users/login" указывает клиенту (например, документации /docs), по какому эндпоинту можно получить токен.
# Сама зависимость не вызывает этот эндпоинт, а только извлекает токен из запроса.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# Хеширование и проверка пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Создание JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()  # копируем, чтобы не изменять исходный словарь
    # Устанавливаем время истечения токена
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire}) # добавляем поле exp (expiration time) в payload
    # Кодируем payload в JWT с секретным ключом и алгоритмом
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Получение текущего пользователя по токену
async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)):
    """
    Извлекает текущего пользователя из JWT токена.
    Используется как зависимость в защищённых эндпоинтах.
    :param token: токен, автоматически извлечённый из заголовка Authorization благодаря oauth2_scheme
    :param db: сессия базы данных
    :return: объект пользователя (модель User)
    :raises HTTPException: если токен невалиден или пользователь не найден
    """
    # Создаём исключение на случай ошибки аутентификации (будет вызвано в нескольких местах)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем токен: проверяем подпись, срок действия и т.д.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Извлекаем email из поля "sub" (стандартное поле для идентификатора субъекта)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # Создаём объект TokenData (простая Pydantic модель) с email
        token_data = schemas.TokenData(email=email)
    except JWTError:
        # Любая ошибка при декодировании (неверная подпись, просроченный токен, искажённый токен)
        raise credentials_exception
    
    # Ищем пользователя в базе данных по email
    user = await session.execute(select(User).filter(User.email == token_data.email))
    user = user.scalar_one_or_none()
    if user is None:
        # Пользователь мог быть удалён после выдачи токена
        raise credentials_exception
    return user


# Зависимость для проверки роли администратора
async def get_current_admin(
        current_user: User = Depends(get_current_user)
):
    # Проверяем, что у пользователя есть роль администратора
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user