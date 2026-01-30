import os
import redis
from typing import Optional

from app.logger import get_logger


logger = get_logger("yaplate.redis")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """
    Return a singleton Redis client.

    Lazily initialized and reused across the app.
    """
    global _redis

    if _redis is None:
        try:
            _redis = redis.Redis.from_url(
                REDIS_URL,
                decode_responses=True,
            )
        except redis.RedisError as exc:
            logger.exception("Failed to create Redis client")
            raise exc

    return _redis
