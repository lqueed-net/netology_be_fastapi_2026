from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import router


# Обработчики событий жизненного цикла
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск приложения
    print("Приложение запускается...")
    
    yield
    
    # Завершение работы
    print("Приложение завершает работу...")

# Создание экземпляра FastAPI
app = FastAPI(
    title="Student API",
    description="Простое FastAPI приложение для студентов",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
    )