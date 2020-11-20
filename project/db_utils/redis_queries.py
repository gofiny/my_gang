from aioredis import Redis
from db_utils.models import Player, Fight
from typing import Optional


async def add_player(pool: Redis, player: Player) -> None:
    await pool.set(f"player:{player.uuid}", player.serialize())


async def remove_player(pool: Redis, player: Player) -> None:
    await pool.delete(f"player:{player.uuid}")


async def get_await_fight(pool: Redis) -> Optional[Fight]:
    fight = await pool.getset(key="fight", value="", encoding="utf-8")
    if fight == "":
        return None
    return Fight(data=fight)


async def check_fight(pool: Redis) -> Optional[Fight]:
    fight = await pool.get(key="fight", encoding="utf-8")
    if fight == "":
        return None
    return Fight(data=fight)


async def add_await_fight(pool: Redis, fight: Optional[Fight] = None) -> None:
    await pool.set("fight", fight.serialize() if fight else "")


async def get_player(pool: Redis, player_uuid: str) -> Optional[Player]:
    data = await pool.get(key=f"player:{player_uuid}", encoding="utf-8")
    if data:
        return Player(data=data, from_redis=True, need_deserialize=True)
    return data


async def get_all_players(pool: Redis) -> list:
    keys = await pool.keys(pattern="player:*", encoding="utf-8")
    if keys:
        return await pool.mget(*keys, encoding="utf-8")
    return []
