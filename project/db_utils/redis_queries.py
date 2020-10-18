from loguru import logger
from aioredis import Redis
from db_utils.models import Player
from typing import Optional


async def add_player(pool: Redis, player: Player) -> None:
    await pool.hmset_dict(f"player:{player.uuid}", player.all_params)


async def get_player(pool: Redis, player_uuid: str) -> Optional[Player]:
    data = await pool.hgetall(key=f"player:{player_uuid}", encoding="utf-8")
    logger.debug(f"{data}")
    if data:
        return Player(data=data, from_redis=True)
    return data
