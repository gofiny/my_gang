import asyncpg
from asyncpg.pool import Pool
import aioredis
from aioredis import Redis
from db_utils.models import User
from db_utils import redis_queries, pg_queries
from aiohttp.web import Application, Response, Request, post, run_app
from vk_api.vk import VK, Message


class WebApp:
    def __init__(
            self, tlg_address_prefix: str, vk_address_prefix: str,
            secret_str: str, returning_callback_str: str, bot: VK
    ):
        self.bot = bot
        self.secret_str = secret_str
        self.app = Application()
        self.returning_callback_str = returning_callback_str
        self._set_base_handlers(tlg_address_prefix=tlg_address_prefix, vk_address_prefix=vk_address_prefix)

    def _set_base_handlers(self, tlg_address_prefix: str, vk_address_prefix: str):
        self.app.add_routes([post(f"/{vk_address_prefix}/", self._vk_base_handler)])
        self.app.add_routes([post(f"/{tlg_address_prefix}/", self._vk_base_handler)])

    async def _vk_base_handler(self, request: Request) -> Response:
        request_json = await request.json()
        if request_json.get("secret") != self.secret_str:
            return Response(status=404)
        request_type = request_json["type"]
        if request_type == "confirmation":
            return Response(body=self.returning_callback_str)
        elif request_type == "message_new":
            message_object = self._get_message_object(request_json)
            await self._process_new_message(message_object)

        return Response(body="ok")

    async def _tlg_base_handler(self, request: Request) -> Response:
        return Response(body="ok")

    @staticmethod
    def _call_filter(message: Message) -> str:
        if message.payload:
            payload = message.payload
            if payload.get("command"):
                _filter = f'payload_{payload["command"]}'
            else:
                _filter = f'text_{message.text}'
        else:
            _filter = f'text_{message.text}'

        return _filter

    @staticmethod
    def _get_message_object(request_object: dict) -> dict:
        return request_object["object"]["message"]

    def get_pg_pool(self) -> Pool:
        return self.app["pg_pool"]

    def get_redis_pool(self) -> Redis:
        return self.app["redis_pool"]

    async def _get_pg_user(self, user_id: int) -> User:
        pool = self.get_pg_pool()
        async with pool.acquire() as connection:
            return await pg_queries.get_or_create_user(connection=connection, user_id=user_id)

    async def _get_user(self, user_id: int):
        user = await redis_queries.get_user_or_none(pool=self.get_redis_pool(), user_id=user_id)
        if not user:
            user = await self._get_pg_user(user_id=user_id)
        return user

    async def _process_new_message(self, message_object: dict) -> None:
        user = await self._get_user(user_id=message_object["from_id"])
        message = self._create_message(message_object, user=user)
        _filter = self._call_filter(message)
        func = self.bot.handlers.get(_filter, self.bot.handlers.get("text_*"))
        if func:
            await func(message)

    async def _create_pg_tables(self) -> None:
        pool = self.get_pg_pool()
        async with pool.acquire() as connection:
            await pg_queries.preparing_db(connection=connection)

    async def prepare(self, postgres_dsn: str, redis_address: str) -> None:
        self.app["pg_pool"] = await asyncpg.create_pool(dsn=postgres_dsn)
        self.app["redis_pool"] = await aioredis.create_redis_pool(redis_address)
        await self._create_pg_tables()

    @staticmethod
    async def _on_shutdown(app: Application) -> None:
        await app["pg_pool"].close()
        await app["redis_pool"].close()

    def _create_message(self, message_object: dict, user: User) -> Message:
        return Message(bot=self.bot, message_json=message_object, user=user)

    def start_app(self, socket_path=None):
        self.app.on_shutdown.append(self._on_shutdown)
        run_app(self.app, path=socket_path)
