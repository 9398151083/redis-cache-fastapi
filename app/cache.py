import json
from fastapi import Request
from app.redis_client import redis_client

DEFAULT_CACHE_TTL = 120  # seconds


def build_cache_key(request: Request) -> str:
    """
    Build a stable cache key from request
    """
    return f"cache:{request.method}:{request.url.path}?{request.url.query}"


async def get_cache(request: Request):
    """
    Get cached response if exists
    """
    cache_key = build_cache_key(request)
    cached = redis_client.get(cache_key)

    if cached:
        print(f"[CACHE HIT] {cache_key}")
        data = json.loads(cached)
        data["source"] = "redis"
        return data

    print(f"[CACHE MISS] {cache_key}")
    return None


async def set_cache(request: Request, data, ttl: int = DEFAULT_CACHE_TTL):
    """
    Store response in Redis cache
    """
    cache_key = build_cache_key(request)
    redis_client.setex(cache_key, ttl, json.dumps(data))


def invalidate_cache(pattern: str):
    """
    Delete all cache keys matching a pattern
    """
    print(f"[CACHE INVALIDATION] Pattern: {pattern}")
    for key in redis_client.scan_iter(pattern):
        print(f"[CACHE DELETE] {key}")
        redis_client.delete(key)
