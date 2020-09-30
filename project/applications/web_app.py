import asyncpg
import aioredis
from db_utils.models import User
from db_utils import redis_queries
from aiohttp.web import Application, Response, Request, post, run_app
from vk_api.vk import VK, Message


class WebApp:
    def __init__(self, address_prefix: str,  secret_str: str, returning_callback_str: str, bot: VK):
        self.bot = bot
        self.secret_str = secret_str
        self.app = Application()
        self.returning_callback_str = returning_callback_str
        self._set_base_handler(address_prefix=address_prefix)

    def _set_base_handler(self, address_prefix: str):
        self.app.add_routes([post(f"/{address_prefix}/", self._base_handler)])

    async def _base_handler(self, request: Request) -> Response:
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

    async def _process_new_message(self, message_object: dict) -> None:
        user = await redis_queries.return_or_create_user(pool=self.app["redis_pool"], user_id=message_object["from_id"])
        message = self._create_message(message_object, user=user)
        _filter = self._call_filter(message)
        func = self.bot.handlers.get(_filter, self.bot.handlers.get("text_*"))
        if func:
            await func(message)

    async def prepare(self, postgres_dsn: str, redis_address: str) -> None:
        #self.app["pq_pool"] = await asyncpg.create_pool(dsn=postgres_dsn)
        self.app["redis_pool"] = await aioredis.create_redis_pool(redis_address)

    async def _on_clean_up(self) -> None:
        await self.app.get("pg_pool").close()
        #await self.app.get("redis_pool").close()

    def _create_message(self, message_object: dict, user: User) -> Message:
        return Message(bot=self.bot, message_json=message_object, user=user)

    def start_app(self, socket_path=None):
        self.app.on_cleanup.append(self._on_clean_up)
        run_app(self.app, path=socket_path)
