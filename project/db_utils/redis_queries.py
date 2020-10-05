from aioredis import Redis
from typing import Optional
from db_utils.models import Player


async def get_user_or_none(pool: Redis, user_id: int) -> Optional[Player]:
    user = await pool.hgetall(key=f"users:{user_id}", encoding="utf-8")
    if user:
        return Player(user)
    return None
