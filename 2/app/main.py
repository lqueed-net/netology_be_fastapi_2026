from fastapi import FastAPI
from contextlib import asynccontextmanager

from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Starting app')

    yield

    print('Closing app')


app = FastAPI(
    title="Test API",
    description="my test app",
    version="1.0.0",
)
app.include_router(router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host='localhost',
        port=8000
    )