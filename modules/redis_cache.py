import redis.asyncio as redis
import os
import json

redis_client = redis.from_url(os.getenv("REDIS_URL"))

async def get(key: str) -> dict|None:
  data = await redis_client.get(key)
  if not data:
    return None
  return json.loads(data)

async def set(key: str, value: dict, delete_time_seconds: int = 30) -> None:
  await redis_client.set(key, json.dumps(value), ex=delete_time_seconds)
