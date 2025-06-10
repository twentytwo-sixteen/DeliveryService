from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from src.app.core.config import get_settings

settings = get_settings()

async def init_cache():
    redis = aioredis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}", 
        encoding="utf8", 
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
