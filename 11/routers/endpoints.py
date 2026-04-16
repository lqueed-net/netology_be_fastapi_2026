from fastapi import APIRouter
import time
from datetime import datetime
import json


from cache_tools.cache import RedisCache
from functools import lru_cache
from functools import wraps

from loguru import logger

router = APIRouter()


# Initialize Redis cache
redis_cache = RedisCache()


def expensive_computation(n: int) -> dict:
    """Simulate expensive computation"""
    # Simulate CPU intensive work
    result = 0
    for i in range(n * 100000):
        result += i % 100

    return {
        "input": n,
        "result": result,
        "computed_at": datetime.now()
    }


def get_user_data(user_id: str) -> dict:
    """Simulate database fetch with some processing"""
    # Simulate database delay
    time.sleep(0.2)
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "profile": {
            "age": (hash(user_id) % 50) + 18,
            "city": f"City {hash(user_id) % 10}"
        },
        "last_accessed": datetime.now()
    }


def measure_time(endpoint_func):
    """Декоратор для измерения времени выполнения эндпоинта"""

    @wraps(endpoint_func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        # Выполнение оригинальной функции
        result = await endpoint_func(*args, **kwargs)

        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000
        elapsed_ms_str = f'{elapsed_ms:.2f}ms'

        logger.info(f"Endpoint {endpoint_func.__name__} executed in {elapsed_ms_str}")

        if isinstance(result, dict):
            result['work_time'] = elapsed_ms_str
        return result

    return wrapper

@lru_cache(maxsize=128)
def sum_of_squares(n: int) -> int:
    """
    Вычисляет сумму квадратов чисел от 1 до n.
    Намеренно неоптимальная реализация для нагрузки на CPU.
    """
    total = 0
    for i in range(1, n + 1):
        # Вложенный цикл для квадратичной сложности
        for j in range(i):
            total += i
    return total


@router.get("/compute/{n}")
@measure_time
async def compute_with_caching(n: int):
    """Endpoint demonstrating local LRU cache with functools.lru_cache"""

    # This will be cached after first call for each n
    result = sum_of_squares(n)

    return {
        "input": n,
        "result": result,
        "cache_info": str(sum_of_squares.cache_info()),
    }

@router.get("/users/{user_id}")
@measure_time
async def get_user_with_redis_cache(user_id: str):
    """Endpoint demonstrating Redis cache"""
    cache_key = f"user:{user_id}"
    t_start = time.perf_counter()
    # Try to get from Redis cache first
    cached_result = redis_cache.get(cache_key)
    if cached_result:
        try:
            user_data = json.loads(cached_result)

            computation_time = time.perf_counter() - t_start
            return {
                "user": user_data,
                "cached": True,
                "source": "Redis",
            }
        except:
            pass

    # If not in cache, fetch from "database"
    user_data = get_user_data(user_id)

    # Store in Redis cache for 5 minutes
    try:
        redis_cache.set(cache_key, json.dumps(user_data), expire=300)
    except:
        pass

    computation_time = time.perf_counter() - t_start

    return {
        "user": user_data,
        "cached": False,
        "source": "Database",
    }

@router.get("/heavy/{n}")
@measure_time
async def expensive_operation(n: int):
    """Endpoint demonstrating manual LRU cache implementation"""
    cache_key = f"expensive:{n}"
    # Try Redis cache first
    cached_result = redis_cache.get(cache_key)
    if cached_result:
        try:
            result = json.loads(cached_result)
            return {
                "result": result,
                "cached": True,
                "source": "Redis"
            }
        except:
            pass

    # Simulate expensive computation
    result = expensive_computation(n)

    # Store in Redis cache
    try:
        redis_cache.set(cache_key, json.dumps(result), expire=300)
    except:
        pass

    return {
        "result": result,
        "cached": False,
        "source": "Computed"
    }


@router.post("/cache/clear")
@measure_time
async def clear_cache():
    """Clear all caches"""
    # Clear functools.lru_cache
    sum_of_squares.cache_clear()

    # Clear Redis cache if available
    if redis_cache.client:
        try:
            redis_cache.client.flushdb()
        except:
            pass

    return {"message": "All caches cleared"}

@router.get("/cache/info")
@measure_time
async def cache_info():
    """Get cache information"""
    return {
        "lru_cache": str(sum_of_squares.cache_info()),
        "redis_available": redis_cache.client is not None
    }