import asyncio
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
import aioredis
from aioredis import Redis
from db_utils import pg_queries, redis_queries
from db_utils.models import Player
from time import time
import config


class Manager:
    def __init__(self):
        self.storage = {}

    async def prepare(self):
        self.storage["pg_pool"] = await asyncpg.create_pool(dsn=config.PG_DESTINATION)
        self.storage["redis"] = await aioredis.create_redis_pool(config.REDIS_ADDRESS)

    @property
    def pg_pool(self) -> Pool:
        return self.storage["pg_pool"]

    @property
    def redis(self) -> Redis:
        return self.storage["redis"]

    @staticmethod
    async def get_player(players: list):
        for player in players:
            yield Player(data=player, from_redis=True)

    async def find_afk(self):
        players = await redis_queries.get_all_players(pool=self.redis)
        async for player in self.get_player(players):
            if (player.counters.lm_time + 1200) > time():
                pass
