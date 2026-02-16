import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()

# Create a lazy-loaded redis client
_redis_client = None

async def get_redis_client():
    """Get or create the redis client lazily"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _redis_client

# For backward compatibility, create a simple wrapper
class RedisClientProxy:
    async def set(self, *args, **kwargs):
        client = await get_redis_client()
        return await client.set(*args, **kwargs)
    
    async def get(self, *args, **kwargs):
        client = await get_redis_client()
        return await client.get(*args, **kwargs)
    
    async def delete(self, *args, **kwargs):
        client = await get_redis_client()
        return await client.delete(*args, **kwargs)

redis_client = RedisClientProxy()

async def get_redis():
    """Dependency to provide the redis client"""
    return redis_client