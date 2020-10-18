from aioredis import Redis
from db_utils.models import Player
from typing import Optional


async def add_player(pool: Redis, player: Player) -> None:
    await pool.set(f"player:{player.uuid}", player.serialize())


async def get_player(pool: Redis, player_uuid: str) -> Optional[Player]:
    data = await pool.get(key=f"player:{player_uuid}", encoding="utf-8")
    if data:
        return Player(data=data, from_redis=True)
    return data
