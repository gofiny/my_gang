from time import time
from asyncpg import Connection, Record
from asyncpg.pool import Pool
from db_utils.models import Player
from typing import Optional
from uuid import uuid4
from db_utils import sql


def transaction(func):
    async def wrapper(*args, **kwargs):
        params = {**kwargs}
        connection: Connection = params.get("connection")
        pool: Pool = params.get("pool")
        if connection:
            async with connection.transaction():
                result = await func(*args, **kwargs)
        else:
            async with pool.acquire() as connection:
                async with connection.transaction():
                    result = await func(*args, **kwargs)
        return result
    return wrapper


@transaction
async def preparing_db(connection: Connection):
    await connection.execute(sql.create_players_table)


@transaction
async def get_player_uuid(connection: Connection, user_id: int, prefix: str) -> Optional[str]:
    user_uuid = await connection.fetchrow(sql.select_pl_uuid_by_user_id % prefix, user_id)
    if user_uuid:
        user_uuid = user_uuid["uuid"]
    return user_uuid


async def _get_player_with_stuff(connection: Connection, user_id: int, prefix: str) -> Record:
    return await connection.fetchrow(sql.select_player_and_stuff % prefix, user_id)


async def _create_new_player(connection: Connection, user_id: int, username: str, prefix: str) -> None:
    return await connection.fetchrow(
        sql.create_new_player_with_stuff % prefix,
        uuid4(), user_id, username, uuid4(), uuid4(), int(time())
    )


@transaction
async def create_player_and_return(connection: Connection, user_id: int) -> Player:
    user = await _get_user(connection, user_id)
    if not user:
        user = await _create_new_player(connection, user_id)
    return Player(dict(user))
