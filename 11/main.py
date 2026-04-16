from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import endpoints

app = FastAPI(
    title="FastAPI Demo",
    description="Пример сервиса с кешированием",
    version="0.1.0",
)

# Обработчики событий жизненного цикла
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск приложения
    print("Приложение запускается...")
    print("Инициализация кэшей...")
    # Создаем таблицы в базе данных
    yield
    # Завершение работы
    print("Приложение завершает работу...")

# Подключение роутеров
app.include_router(endpoints.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
    )