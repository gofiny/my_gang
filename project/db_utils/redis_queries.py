from aioredis import Redis
from db_utils.models import Player, Fight
from typing import Optional
from loguru import logger


async def add_player(pool: Redis, player: Player) -> None:
    await pool.set(f"player:{player.uuid}", player.serialize())


async def get_await_fight(pool: Redis) -> Optional[str]:
    fight = await pool.getset(key="fight", value="", encoding="utf-8")
    logger.info(f"{fight}")
    if fight == "":
        return None
    return fight


async def add_await_fight(pool: Redis, fight: Optional[Fight]) -> None:
    await pool.set("fight", fight.serialize() if fight else "")


async def get_player(pool: Redis, player_uuid: str) -> Optional[Player]:
    data = await pool.get(key=f"player:{player_uuid}", encoding="utf-8")
    if data:
        return Player(data=data, from_redis=True)
    return data
