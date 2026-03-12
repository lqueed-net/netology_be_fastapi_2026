from fastapi import FastAPI
from routers import items, items_orders
from contextlib import asynccontextmanager

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

    yield

    # Завершение работы
    print("Приложение завершает работу...")


app.include_router(items.router)
app.include_router(items_orders.router_orders)
app.include_router(items_orders.router_order_items)

@app.get("/")
async def root():
    return {"message": "Hello, SOLID!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
    )