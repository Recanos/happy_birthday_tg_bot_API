from fastapi import FastAPI
from operations.router import router as router_operations
from tasks.router import router as router_tasks
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis

app = FastAPI(
    title="Happy Birthday!",
    description="API для управления пользователями и подписками на дни рождения с использованием FastAPI и SQLAlchemy",
)

app.include_router(router_operations)
app.include_router(router_tasks)

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

