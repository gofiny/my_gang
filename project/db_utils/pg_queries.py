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
    await connection.execute(sql.create_goods_table)
    await connection.execute(sql.create_event_table)
    is_created = await connection.fetchval(sql.check_goods, "watch")
    if not is_created:
        goods = [
            (uuid4(), "watch", "\U0000231A часы", 30, 50),
            (uuid4(), "phone", "\U0001F4F1 телефоны", 30, 300),
            (uuid4(), "headphones", "\U0001F3A7 наушники", 30, 20),
            (uuid4(), "credit_card", "\U0001F4B3 кредитки", 30, 30),
            (uuid4(), "glasses", "\U0001F453 очки", 30, 30),
            (uuid4(), "cap", "\U0001F9E2 кепки", 30, 15),
            (uuid4(), "gloves", "\U0001F9E4 перчатки", 30, 10),
        ]
        await connection.executemany(sql.create_goods, goods)


@transaction
async def get_player_uuid(connection: Connection, user_id: int, prefix: str) -> Optional[str]:
    user_uuid = await connection.fetchrow(sql.select_pl_uuid_by_user_id % prefix, user_id)
    if user_uuid:
        user_uuid = str(user_uuid["uuid"])
    return user_uuid


@transaction
async def get_player_with_stuff(connection: Connection, player_uuid: str, current_platform: str) -> Player:
    player_data = await connection.fetchrow(sql.select_player_and_stuff, player_uuid)
    player_data = dict(player_data)
    player_data["current_platform"] = current_platform
    player = Player(data=player_data)
    return player


@transaction
async def create_new_player(connection: Connection, user_id: int, prefix: str) -> str:
    player_uuid = await connection.fetchrow(
        sql.create_new_player_with_stuff % prefix,
        uuid4(), user_id, uuid4(), uuid4(), int(time()), uuid4(), uuid4()
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


@transaction
async def update_player(connection: Connection, player: Player) -> None:
    await connection.execute(sql.update_player,
                             player.level.level, player.health, player.power, player.mind, player.respect, player.uuid,
                             player.counters.lm_time, player.counters.daily_actions, player.counters.total_actions,
                             player.storage.watch, player.storage.phone, player.storage.headphones,
                             player.storage.credit_card, player.storage.glasses, player.storage.cap,
                             player.storage.gloves,
                             player.event_stuff.upgrade_block,
                             player.wallet.dollars)


async def open_connection(pool: Pool, func: Callable, *args, **kwargs) -> Optional[Any]:
    async with pool.acquire() as connection:
        val = await func(connection=connection, *args, **kwargs)
        if val:
            return val
