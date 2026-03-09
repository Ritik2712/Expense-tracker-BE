import json
import os
from typing import Any

import redis
from fastapi.encoders import jsonable_encoder


REDIS_URL = os.getenv("REDIS_URL")
_client = redis.Redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else None


def cache_enabled() -> bool:
    return _client is not None


def get_cache(key: str) -> Any | None:
    if not _client:
        return None
    value = _client.get(key)
    return json.loads(value) if value else None


def set_cache(key: str, value: Any, ttl_seconds: int = 60) -> None:
    if not _client:
        return
    payload = jsonable_encoder(value)
    _client.setex(key, ttl_seconds, json.dumps(payload))


def delete_cache(key: str) -> None:
    if not _client:
        return
    _client.delete(key)


def delete_by_prefix(prefix: str) -> None:
    if not _client:
        return
    for key in _client.scan_iter(f"{prefix}*"):
        _client.delete(key)
