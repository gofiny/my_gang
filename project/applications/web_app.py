import asyncio
import asyncpg
import aioredis
import itertools
import functools
from common_utils import exceptions
from asyncpg import Connection
from asyncpg.pool import Pool
from aioredis import Redis
from aiogram import types
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.webhook import BaseResponse
from db_utils.models import Player
from db_utils import redis_queries, pg_queries
from aiohttp.web import Application, Response, Request, post, run_app, View
from vk_api.vk import VK, Message
from typing import Optional


class WebhookRequestHandler(View):
    def get_dispatcher(self):
        dp = self.request.app['dp']
        try:
            Dispatcher.set_current(dp)
            Bot.set_current(dp.bot)
        except RuntimeError:
            pass
        return dp

    async def parse_update(self):
        data = await self.request.json()
        update = types.Update(**data)
        return update

    async def post(self):

        update = await self.parse_update()

        results = await self.process_update(update)
        response = self.get_response(results)

        if response:
            web_response = response.get_web_response()
        else:
            web_response = Response(text='ok')

        if self.request.app.get('RETRY_AFTER', None):
            web_response.headers['Retry-After'] = self.request.app['RETRY_AFTER']

        return web_response

    @staticmethod
    async def get():
        return Response(text='')

    @staticmethod
    async def head():
        return Response(text='')

    async def process_update(self, update):

        dispatcher = self.get_dispatcher()
        loop = dispatcher.loop or asyncio.get_event_loop()

        waiter = loop.create_future()
        timeout_handle = loop.call_later(55, asyncio.tasks._release_waiter, waiter)
        cb = functools.partial(asyncio.tasks._release_waiter, waiter)

        fut = asyncio.ensure_future(dispatcher.updates_handler.notify(update), loop=loop)
        fut.add_done_callback(cb)

        try:
            try:
                await waiter
            except asyncio.CancelledError:
                fut.remove_done_callback(cb)
                fut.cancel()
                raise

            if fut.done():
                return fut.result()
            else:

                fut.remove_done_callback(cb)
                fut.add_done_callback(self.respond_via_request)
        finally:
            timeout_handle.cancel()

    def respond_via_request(self, task):
        dispatcher = self.get_dispatcher()
        loop = dispatcher.loop or asyncio.get_event_loop()

        try:
            results = task.result()
        except Exception as e:
            loop.create_task(
                dispatcher.errors_handlers.notify(dispatcher, types.Update.get_current(), e))
        else:
            response = self.get_response(results)
            if response is not None:
                asyncio.ensure_future(response.execute_response(dispatcher.bot), loop=loop)

    @staticmethod
    def get_response(results):
        if results is None:
            return None
        for result in itertools.chain.from_iterable(results):
            if isinstance(result, BaseResponse):
                return result


class WebApp:
    def __init__(
            self, tlg_address_prefix: str, vk_address_prefix: str,
            secret_str: str, returning_callback_str: str,
            vk_bot: VK, tlg_dp: Dispatcher
    ):
        self.vk_bot = vk_bot
        self.tlg_dp = tlg_dp
        self.secret_str = secret_str
        self.app = Application()
        self.returning_callback_str = returning_callback_str
        self._set_base_handlers(tlg_address_prefix=tlg_address_prefix, vk_address_prefix=vk_address_prefix)

    def _set_base_handlers(self, tlg_address_prefix: str, vk_address_prefix: str):
        self.app.add_routes([post(f"/{vk_address_prefix}/", self._vk_base_handler)])
        self.app.add_routes([post(f"/{tlg_address_prefix}/", WebhookRequestHandler)])

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

    @staticmethod
    async def register_player(connection: Connection, user_id: int, prefix: str) -> str:
        return await pg_queries.create_new_player(connection=connection, user_id=user_id, prefix=prefix)

    @staticmethod
    async def get_player_from_pg(connection: Connection, player_uuid: str) -> Player:
        return await pg_queries.get_player_with_stuff(connection=connection, player_uuid=player_uuid)

    async def add_player_to_redis(self, player: Player):
        pool = await self.get_redis_pool()
        await redis_queries.add_player(pool=pool, player=player)

    async def check_player(self, user_id: int, prefix):
        pool = await self.get_pg_pool()
        async with pool.acquire() as connection:
            user_uuid = await pg_queries.get_player_uuid(connection=connection, user_id=user_id, prefix=prefix)
            if not user_uuid:
                player_uuid = await self.register_player(connection=connection, user_id=user_id, prefix=prefix)
                player = await self.get_player_from_pg(connection=connection, player_uuid=player_uuid)
                await self.add_player_to_redis(player=player)
                raise exceptions.PlayerNotRegistered
            return user_uuid

    async def get_player_from_redis(self, player_uuid: str) -> Player:
        pool = self.get_redis_pool()
        player = await redis_queries.get_player(pool=pool, player_uuid=player_uuid)
        if not player:
            raise exceptions.DisconnectedPlayer
        return player

    async def get_player(self, user_id: int, prefix: str = "vk") -> Player:
        player_uuid = await self.check_player(user_id=user_id, prefix=prefix)
        player = await self.get_player_from_redis(player_uuid=player_uuid)
        return player

    async def _process_new_message(self, message_object: dict) -> None:
        try:
            player = await self.get_player(user_id=message_object["from_id"])
            message = self._create_message(message_object, player=player)
            _filter = self._call_filter(message)
            func = self.vk_bot.handlers.get(_filter, self.vk_bot.handlers.get("text_*"))
        except exceptions.PlayerNotRegistered:
            func = self.vk_bot.handlers.get("payload_register")
            message = self._create_message(message_object)
        except exceptions.DisconnectedPlayer:
            func = self.vk_bot.handlers.get("payload_disconnected")
            message = self._create_message(message_object)

        if func:
            await func(message)

    async def _create_pg_tables(self) -> None:
        pool = self.get_pg_pool()
        async with pool.acquire() as connection:
            await pg_queries.preparing_db(connection=connection)

    async def prepare(self, postgres_dsn: str, redis_address: str) -> None:
        self.app["web_app"] = self
        self.app["vk_bot"] = self.vk_bot
        self.app["pg_pool"] = await asyncpg.create_pool(dsn=postgres_dsn)
        self.app["redis_pool"] = await aioredis.create_redis_pool(redis_address, encoding="utf-8")
        self.app["dp"] = self.tlg_dp
        await self._create_pg_tables()

    @staticmethod
    async def _on_shutdown(app: Application) -> None:
        vk_bot: VK = app["vk_bot"]
        pg_pool: Pool = app["pg_pool"]
        redis_pool: Redis = app["redis_pool"]

        redis_pool.close()
        await redis_pool.wait_closed()
        await pg_pool.close()
        await vk_bot.clean_up()

    def _create_message(self, message_object: dict, player: Optional[Player] = None) -> Message:
        return Message(bot=self.vk_bot, message_json=message_object, player=player)

    def start_app(self, socket_path=None):
        self.app.on_shutdown.append(self._on_shutdown)
        run_app(self.app, path=socket_path)
