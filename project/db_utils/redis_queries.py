from aioredis import Redis
from typing import Optional
from db_utils.models import User


async def return_user_or_none(pool: Redis, user_id: int) -> Optional[User]:
    user = await pool.hgetall(key=f"users:{user_id}", encoding="utf-8")
    if user:
        return User(user)
    return None


async def add_user(pool: Redis, user_id: int):
    user = {"user_id": user_id, "if_followed": 0}
    await pool.hmset_dict(f"users:{user['user_id']}", user)
