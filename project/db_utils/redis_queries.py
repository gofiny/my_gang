from aioredis import Redis
from typing import Optional
from db_utils.models import User


async def get_user_or_none(pool: Redis, user_id: int) -> Optional[User]:
    user = await pool.hgetall(key=f"pusers:{user_id}", encoding="utf-8")
    if user:
        return User(user)
    return None


async def add_user(pool: Redis, user: User) -> None:
    user = {"user_id": user.user_id, "if_followed": user.is_followed}
    await pool.hmset_dict(f"pusers:{user['user_id']}", user)


async def change_subscribe(pool: Redis, user: User):
    await pool.hset(f"pusers:{user.user_id}", "is_followed", user.is_followed)
