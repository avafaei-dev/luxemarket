import json
import logging
from typing import Any

import redis
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global Redis client — created once, reused across requests
_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis | None:
    """Return Redis client, or None if Redis is unavailable."""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            _redis_client.ping()
            logger.info("Redis connected at %s", settings.redis_url)
        except Exception as e:
            logger.warning("Redis unavailable: %s — caching disabled", e)
            _redis_client = None
    return _redis_client


def cache_get(key: str) -> Any | None:
    """Get a value from cache. Returns None on miss or error."""
    r = get_redis()
    if r is None:
        return None
    try:
        raw = r.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.warning("Cache get error for key %s: %s", key, e)
        return None


def cache_set(key: str, value: Any, ttl: int = 60) -> None:
    """Set a value in cache with a TTL in seconds. Silently fails."""
    r = get_redis()
    if r is None:
        return
    try:
        r.setex(key, ttl, json.dumps(value, default=str))
    except Exception as e:
        logger.warning("Cache set error for key %s: %s", key, e)


def cache_delete(key: str) -> None:
    """Delete a key from cache."""
    r = get_redis()
    if r is None:
        return
    try:
        r.delete(key)
    except Exception as e:
        logger.warning("Cache delete error for key %s: %s", key, e)


def cache_flush_pattern(pattern: str) -> int:
    """Delete all keys matching a pattern. Returns count deleted."""
    r = get_redis()
    if r is None:
        return 0
    try:
        keys = r.keys(pattern)
        if keys:
            return r.delete(*keys)
        return 0
    except Exception as e:
        logger.warning("Cache flush error for pattern %s: %s", pattern, e)
        return 0


def make_cache_key(*parts: str) -> str:
    """Build a namespaced cache key from parts."""
    return "luxemarket:" + ":".join(str(p) for p in parts)
