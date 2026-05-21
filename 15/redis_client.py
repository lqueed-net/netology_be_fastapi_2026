import redis.asyncio as redis
import os

# Global Redis client instance
redis_client = None

async def init_redis():
    """Initialize Redis client"""
    global redis_client
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    return redis_client

async def close_redis():
    """Close Redis client connection"""
    global redis_client
    if redis_client:
        await redis_client.close()