#!/usr/bin/env python3
"""
Test script for Redis caching functionality
"""

import asyncio
import json
import os
import redis.asyncio as redis

async def test_redis_connection():
    """Test Redis connection and basic operations"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    try:
        # Connect to Redis
        redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        print(f"Connected to Redis at {redis_url}")

        # Test ping
        pong = await redis_client.ping()
        print(f"Ping result: {pong}")

        # Test set/get
        test_key = "test:key"
        test_value = {"name": "Test Item", "price": 99.99}

        await redis_client.setex(test_key, 60, json.dumps(test_value))
        print(f"Set {test_key} = {test_value}")

        cached_value = await redis_client.get(test_key)
        if cached_value:
            parsed_value = json.loads(cached_value)
            print(f"Retrieved {test_key} = {parsed_value}")

        # Clean up
        await redis_client.delete(test_key)
        print(f"Deleted {test_key}")

        # Close connection
        await redis_client.close()
        print("Redis connection test completed successfully!")

    except Exception as e:
        print(f"Redis connection test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_redis_connection())