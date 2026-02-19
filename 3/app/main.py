from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import router
from routes_validated import router as router_validated


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
app.include_router(router, prefix='/v1')
app.include_router(router_validated, prefix='/v2')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
    )