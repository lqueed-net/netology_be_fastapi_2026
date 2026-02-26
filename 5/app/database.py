from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# URL базы данных (замените на свой)
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:pwd@localhost:5432/test"

# Движок для асинхронной работы
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Базовый класс моделей (синхронный, но подходит для асинхронного использования)
Base = declarative_base()