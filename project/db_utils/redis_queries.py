from aioredis import Redis
from db_utils.models import User


async def return_or_create_user(pool: Redis, user_id: int) -> User:
    is_exist = await pool.exists(key=f"users:{user_id}")
    if is_exist:
        user = await pool.hgetall(key=f"users:{user_id}", encoding="utf-8")
        print(user)
    else:
        user = {"user_id": user_id, "if_followed": False}
        await pool.hmset_dict(f"users:{user['user_id']}", user)
    return User(user)
