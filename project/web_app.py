from aiohttp.web import Application, Response, Request, post, run_app
from vk import VK, Message


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
            await self._process_new_message(request_json)

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

    async def _process_new_message(self, data: dict):
        message = self._create_message(data["object"]["message"])
        _filter = self._call_filter(message)
        func = self.bot.handlers.get(_filter, self.bot.handlers.get("text_*"))
        if func:
            await func(message)

    @staticmethod
    def _create_message(message_object: dict):
        return Message(message_object)

    def start_app(self, socket_path=None):
        run_app(self.app, path=socket_path)
