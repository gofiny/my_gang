from aioredis import Redis
from typing import Optional


async def get_player_states(pool: Redis, vk_id: int = None, tlg_id: int = None) -> Optional[dict]:
    key = f"t"
    states = await pool.hgetall()



