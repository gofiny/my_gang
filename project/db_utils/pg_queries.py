from asyncpg import Connection, Record
from typing import Optional
from db_utils import sql


def transaction(func):
    async def wrapper(connection: Connection, *args, **kwargs):
        async with connection.transaction():
            result = await func(*args, **kwargs)
        return result
    return wrapper


@transaction
async def get_user(connection: Connection, user_id: int) -> Optional[Record]:
    return await connection.fetchrow(sql.select_user_by_user_id(user_id))
