import asyncio
import asyncpg
from aiohttp import ClientSession
from loguru import logger
from asyncpg.pool import Pool
import aioredis
from aioredis import Redis
from db_utils import pg_queries, redis_queries
from db_utils.models import Player
from time import time
import config
import json


class Manager:
    def __init__(self):
        self.storage = {}

    async def prepare(self):
        self.storage["pg_pool"] = await asyncpg.create_pool(dsn=config.PG_DESTINATION, min_size=1, max_size=2)
        self.storage["redis"] = await aioredis.create_redis_pool(config.REDIS_ADDRESS)

    async def on_shutdown(self):
        self.redis.close()
        await self.redis.wait_closed()
        await self.pg_pool.close()

    @property
    def pg_pool(self) -> Pool:
        return self.storage["pg_pool"]

    @property
    def redis(self) -> Redis:
        return self.storage["redis"]

    @staticmethod
    async def send_event(event_name: str, player: Player) -> None:
        data = {"event_name": event_name, "player": player}
        async with ClientSession() as session:
            await session.post(config.EVENTS_ADDR, data=json.dumps(data))

    @staticmethod
    async def get_player(players: list):
        for player in players:
            yield Player(data=player, from_redis=True)

    async def find_afk(self):
        players = await redis_queries.get_all_players(pool=self.redis)
        async with self.pg_pool.acquire() as connection:
            async for player in self.get_player(players):
                logger.debug(f"{player.uuid} is checking")
                if (player.counters.lm_time + 1200) > time():
                    await redis_queries.remove_player(pool=self.redis, player=player)
                    await pg_queries.update_player(connection=connection, player=player)
                    await self.send_event(event_name="afk_disconnect", player=player)
        await asyncio.sleep(10)

    async def main(self):
        try:
            while True:
                await self.find_afk()
        except KeyboardInterrupt:
            await self.on_shutdown()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    manager = Manager()
    try:
        loop.run_until_complete(manager.prepare())
        asyncio.ensure_future(manager.main())
        loop.run_forever()
    finally:
        loop.close()
