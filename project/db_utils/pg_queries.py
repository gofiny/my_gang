from asyncpg import Connection, Record
from typing import Optional
from db_utils import sql


def transaction(func):
    async def wrapper(*args, **kwargs):
        params = {**kwargs}
        connection = params["connection"]
        async with connection.transaction():
            result = await func(*args, **kwargs)
        return result
    return wrapper


@transaction
async def preparing_db(connection: Connection):
    await connection.execute(sql.create_users_table)


@transaction
async def get_user(connection: Connection, user_id: int) -> Optional[Record]:
    return await connection.fetchrow(sql.select_user_by_user_id % user_id)
