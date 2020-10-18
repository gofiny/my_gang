from time import time
from asyncpg import Connection
from asyncpg.pool import Pool
from common_utils import exceptions
from db_utils.models import Player, Wallet
from typing import Optional, Callable, Any
from uuid import uuid4
from db_utils import sql


def transaction(func):
    async def wrapper(*args, **kwargs):
        params = {**kwargs}
        connection: Connection = params.get("connection")
        async with connection.transaction():
            result = await func(*args, **kwargs)
        return result
    return wrapper


@transaction
async def preparing_db(connection: Connection) -> None:
    await connection.execute(sql.create_players_table)
    await connection.execute(sql.create_counters_table)
    await connection.execute(sql.create_wallets_table)
    await connection.execute(sql.create_storage_table)
    seller_uuid = await connection.fetchval(sql.check_seller, "seller")
    if not seller_uuid:
        await connection.execute(sql.create_seller, uuid4(), "seller", uuid4())


@transaction
async def get_player_uuid(connection: Connection, user_id: int, prefix: str) -> Optional[str]:
    user_uuid = await connection.fetchrow(sql.select_pl_uuid_by_user_id % prefix, user_id)
    if user_uuid:
        user_uuid = str(user_uuid["uuid"])
    return user_uuid


@transaction
async def get_player_with_stuff(connection: Connection, player_uuid: str) -> Player:
    player_data = await connection.fetchrow(sql.select_player_and_stuff, player_uuid)
    player_data = dict(player_data)
    player_data["states"] = {"main_state": 0}
    player = Player(data=player_data)
    return player


@transaction
async def create_new_player(connection: Connection, user_id: int, prefix: str) -> str:
    player_uuid = await connection.fetchrow(
        sql.create_new_player_with_stuff % prefix,
        uuid4(), user_id, uuid4(), uuid4(), int(time()), uuid4()
    )
    return str(player_uuid["uuid"])


@transaction
async def set_name_to_player(connection: Connection, name: str, player_uuid: str) -> None:
    name_exists = await connection.fetchval(sql.select_name_from_players, name)
    if name_exists:
        raise exceptions.NameAlreadyExists
    await connection.execute(sql.set_name_to_player, name, player_uuid)


@transaction
async def get_player_wallet(connection: Connection, player_uuid: str) -> Wallet:
    wallet = await connection.fetchrow(sql.select_wallet, player_uuid)
    return Wallet(dict(wallet))


async def open_connection(pool: Pool, func: Callable, *args, **kwargs) -> Optional[Any]:
    async with pool.acquire() as connection:
        val = await func(connection=connection, *args, **kwargs)
        if val:
            return val
