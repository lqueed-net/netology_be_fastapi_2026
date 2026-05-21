import os
from fastapi import FastAPI
from routers import items, items_orders
from contextlib import asynccontextmanager
from redis_client import init_redis, close_redis, redis_client

app = FastAPI(
    title="FastAPI Demo",
    description="Пример приложения FastAPI + CRUD",
    version="0.1.0",
)

# Обработчики событий жизненного цикла
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск приложения
    print("Приложение запускается...")

    # Подключение к Redis
    await init_redis()
    print(f"Подключено к Redis")

    yield

    # Завершение работы
    await close_redis()
    print("Приложение завершает работу...")


app.include_router(items.router)
app.include_router(items_orders.router_orders)
app.include_router(items_orders.router_order_items)

@app.get("/")
async def root():
    return {"message": "Hello, SOLID!"}

# Эндпоинт для проверки кэша Redis
@app.get("/redis-health")
async def redis_health():
    try:
        await redis_client.ping()
        return {"status": "Redis connected"}
    except Exception as e:
        return {"status": "Redis connection failed", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
    )