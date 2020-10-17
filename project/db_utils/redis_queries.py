from loguru import logger
from aioredis import Redis
from db_utils.models import Player
from typing import Optional


async def add_player(pool: Redis, player: Player) -> None:
    transaction = pool.multi_exec()
    # transaction.set(f"player:{player.uuid}", player.serialize())
    # transaction.set(f"wallet:{player.uuid}", player.wallet.serialize())
    # transaction.set(f"counters:{player.uuid}", player.counters.serialize())
    # transaction.set(f"storage:{player.uuid}", player.storage.serialize())
    transaction.hm_dict(f"player:{player.uuid}", player.all_params)
    transaction.hm_dict(f"wallet:{player.uuid}", player.wallet.all_currency)
    transaction.hm_dict(f"counters:{player.uuid}", player.counters.all_counters)
    transaction.hm_dict(f"storage:{player.uuid}", player.storage.all_stuff)
    await transaction.execute()


async def get_player(pool: Redis, player_uuid: str) -> Optional[Player]:
    # data = await pool.get(f"player:{player_uuid}", encoding="utf-8")
    transaction = pool.multi_exec()
    transaction.hgetall(key=f"player:{player_uuid}", encoding="utf-8")
    transaction.hgetall(key=f"wallet:{player_uuid}", encoding="utf-8")
    transaction.hgetall(key=f"counters:{player_uuid}", encoding="utf-8")
    transaction.hgetall(key=f"storage:{player_uuid}", encoding="utf-8")
    data = await transaction.execute()
    logger.info(f"{data}")
    if data[0]:
        return Player(data, wallet=data[1], counters=data[2], storage=data[3], need_deserialize=True)
    return data
