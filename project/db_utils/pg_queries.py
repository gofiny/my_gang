from asyncpg import Connection, Record
from db_utils.models import User
from typing import Optional
from uuid import uuid4
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


async def _get_user(connection: Connection, user_id: int) -> Optional[Record]:
    return await connection.fetchrow(sql.select_user_by_user_id, user_id)


async def _create_new_user(connection: Connection, user_id: int) -> Record:
    return await connection.fetchrow(sql.create_new_user, uuid4(), user_id)


@transaction
async def get_or_create_user(connection: Connection, user_id: int) -> User:
    user = await _get_user(connection, user_id)
    if not user:
        user = await _create_new_user(connection, user_id)
    return User(dict(user))


async def change_subscribe(pool, user: User) -> None:
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(sql.change_subscribe, user.is_followed, user.user_id)
