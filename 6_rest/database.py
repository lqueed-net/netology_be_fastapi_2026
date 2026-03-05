from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Строка подключения
DATABASE_URL = "postgresql+asyncpg://postgres:pwd@localhost:5432/test"

# Создаём асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии в зависимостях FastAPI
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session