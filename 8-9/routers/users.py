from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

import schemas
import auth
from database import get_db
from models import User

router = APIRouter(prefix="/users", tags=["users"])


# Эндпоинт для регистрации нового пользователя.
# Принимает POST-запрос на /users/register.
# request body должен соответствовать схеме UserCreate (email и пароль).
# Ответ возвращает в формате UserOut (id и email, без пароля).
@router.post("/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, session: AsyncSession = Depends(get_db)):
    # user - объект, созданный из тела запроса, автоматически валидированный по схеме UserCreate.
    # session - сессия базы данных, полученная через зависимость get_db.
    
    # 1. Проверяем, не занят ли email.
    # Выполняем запрос к таблице User, фильтруем по email.
    db_user = await session.execute(select(User).filter(User.email == user.email))
    db_user = db_user.scalar_one_or_none()
    # Если пользователь с таким email уже существует (first() вернул объект),
    # выбрасываем исключение HTTPException с кодом 400 и сообщением.
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Хешируем пароль.
    # Вызываем функцию get_password_hash из модуля auth, передаём ей пароль в открытом виде.
    hashed = auth.get_password_hash(user.password)

    # 3. Создаём объект пользователя (модель SQLAlchemy) с email и хешированным паролем.
    new_user = User(email=user.email, hashed_password=hashed)

    # 4. Добавляем объект в сессию, сохраняем в базу, обновляем объект (чтобы получить id).
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # 5. Возвращаем данные созданного пользователя в соответствии со схемой UserOut.
    # Pydantic автоматически преобразует объект new_user благодаря настройке from_attributes = True.
    return new_user


# Эндпоинт для входа в систему (получения JWT токена).
# Принимает POST-запрос на /users/login.
# Использует форму OAuth2 (username/password) благодаря зависимости OAuth2PasswordRequestForm.
# Ответ возвращает объект Token (access_token и token_type).
@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db)):
     # form_data - объект, содержащий поля username и password, отправленные в форме.
    # Мы интерпретируем username как email пользователя.
    # db - сессия базы данных.
    
    # 1. Ищем пользователя в базе по email (form_data.username).
    user = await session.execute(select(User).filter(User.email == form_data.username))
    user = user.scalar_one_or_none()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        # Если пользователь не найден или пароль неверный, возвращаем ошибку 401 Unauthorized.
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Создаём JWT токен.
    # В данные токена (payload) кладём "sub" (subject) со значением email пользователя.
    access_token = auth.create_access_token(data={"sub": user.email})

    # 4. Возвращаем токен согласно схеме Token.
    return {"access_token": access_token, "token_type": "bearer"}


# Эндпоинт для получения информации о текущем аутентифицированном пользователе.
# Принимает GET-запрос на /users/me.
# Требует наличие токена в заголовке Authorization: Bearer <token>.
@router.get("/me", response_model=schemas.UserOut)
async def read_users_me(current_user: User = Depends(auth.get_current_user)):
    # current_user - объект пользователя, полученный из зависимости get_current_user.
    # Эта зависимость извлекает токен, проверяет его валидность, загружает пользователя из БД.
    # Если токен недействителен или пользователь не найден, зависимость сама выбросит исключение.
    
    # Возвращаем данные пользователя в формате UserOut (id, email).
    return current_user


# Эндпоинт для обновления профиля текущего пользователя.
# Принимает PUT-запрос на /users/me.
# Требует наличие токена в заголовке Authorization: Bearer <token>.
@router.put("/me", response_model=schemas.UserOut)
async def update_user_me(
    user_update: schemas.UserUpdate,
    current_user: User = Depends(auth.get_current_user),
    session: AsyncSession = Depends(get_db)
):
    # Обновляем email, если он был передан
    if user_update.email is not None:
        # Проверяем, что новый email не занят другим пользователем
        result = await session.execute(select(User).filter(User.email == user_update.email))
        existing_user = result.scalar_one_or_none()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_update.email

    # Обновляем пароль, если он был передан
    if user_update.password is not None:
        current_user.hashed_password = auth.get_password_hash(user_update.password)

    # Сохраняем изменения в базе данных
    await session.commit()
    await session.refresh(current_user)

    # Возвращаем обновленные данные пользователя
    return current_user

# Эндпоинт для получения списка всех пользователей (только для администраторов).
# Принимает GET-запрос на /users/.
# Требует наличие токена администратора в заголовке Authorization: Bearer <token>.
@router.get("/", response_model=list[schemas.UserOut])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth.get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    # Получаем список пользователей с пагинацией
    result = await session.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users