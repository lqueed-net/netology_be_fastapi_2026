import redis

class RedisCache:
    """Redis cache wrapper"""
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        try:
            self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            # Test connection
            self.client.ping()
        except:
            self.client = None
            print("Redis not available, using dummy cache")

    def get(self, key: str) -> str | None:
        if not self.client:
            return None
        try:
            return self.client.get(key)
        except:
            return None

    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        if not self.client:
            return False
        try:
            return self.client.set(key, value, ex=expire)
        except:
            return False



