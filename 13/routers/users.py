from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

import schemas
import auth
from database import get_db
from models import User

router = APIRouter(prefix="/users", tags=["users"])

# регистрации
@router.post('/register', response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, session: AsyncSession = Depends(get_db)):
    # проверка на занятость email
    db_user = await session.execute(select(User).filter(User.email == user.email))
    db_user = db_user.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')

    # hash password
    hashed = auth.get_password_hash(user.password)

    new_user = User(email=user.email, hashed_password=hashed, role=user.role)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.post('/login', response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db)):
    db_user = await session.execute(select(User).filter(User.email == form_data.username))
    user = db_user.scalar_one_or_none()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password or email",
            headers={'WWW-Authenticate': 'Bearer'}
        )

    # create JWT token
    access_token = auth.create_access_token(data={'sub': user.email})

    # return response
    return {'access_token': access_token, "token_type": 'bearer'}


@router.get('/me', response_model=schemas.UserOut)
async def read_user_me(current_user: User = Depends(auth.get_current_user)):
    return current_user


@router.put('/me', response_model=schemas.UserOut)
async def update_user_me(
        user_update: schemas.UserUpdate,
        current_user: User = Depends(auth.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    # если передан email
    if user_update.email is not None:
        result = await session.execute(select(User).filter(User.email == user_update.email))
        existing_user = result.scalar_one_or_none()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail='Email already registered')
        current_user.email = user_update.email

    # если передан password
    if user_update.password is not None:
        current_user.hashed_password = auth.get_password_hash(user_update.password)

    # save changes
    await session.commit()
    await session.refresh(current_user)

    return current_user

from typing import List
@router.get('/', response_model=List[schemas.UserOut])
async def read_users(
        skip: int = 0,
        limit: int = 10,
        current_user: User = Depends(auth.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Not enough permissions')

    # get list users with pagination
    result = await session.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users





