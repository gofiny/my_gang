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
    await connection.execute(sql.create_counters_table)
    await connection.execute(sql.create_wallets_table)


@transaction
async def get_player_uuid(connection: Connection, user_id: int, prefix: str) -> Optional[str]:
    user_uuid = await connection.fetchrow(sql.select_pl_uuid_by_user_id % prefix, user_id)
    if user_uuid:
        user_uuid = str(user_uuid["uuid"])
    return user_uuid


@transaction
async def get_player_with_stuff(connection: Connection, player_uuid: str) -> Player:
    player_data = await connection.fetchrow(sql.select_player_and_stuff, player_uuid)
    states = {"main_state": 0}
    counters = {
        "lm_time": player_data["lm_time"],
        "daily_actions": player_data["daily_actions"],
        "total_actions": player_data["total_actions"]
    }
    player_data = dict(player_data)
    player_data["states"] = states
    player_data["counters"] = counters
    return Player(player_data)


@transaction
async def create_new_player(connection: Connection, user_id: int, prefix: str) -> str:
    player_uuid = await connection.fetchrow(
        sql.create_new_player_with_stuff % prefix,
        uuid4(), user_id, uuid4(), uuid4(), int(time())
    )
    return str(player_uuid["uuid"])
