import asyncio
from aiohttp import ClientSession
from config import API_KEY, API_VER, GROUP_ID
from vk_api.vk import VK, Message
from typing import Optional
from bot_utils.handlers import bot


class WebApp:
    def __init__(self, vk: VK):
        self._vk_worker = vk
        self.session = ClientSession()
        self.ts = ""
        self.server = ""
        self.key = ""
        self.request_address = ""

    async def _make_request(self, method_name: str, params: dict) -> Optional[dict]:
        _BASE_URL = "https://api.vk.com/method/%s"
        params = {
            **params,
            "access_token": API_KEY,
            "v": API_VER
        }
        async with self.session.get(_BASE_URL % method_name, params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                print(await resp.text())

    def _update_ts(self, new_ts):
        self.ts = new_ts

    @staticmethod
    def _create_message(message_object: dict):
        return Message(message_object)

    async def _get_updates(self, wait_time: int,) -> list:
        params = {
            "ts": self.ts,
            "key": self.key,
            "wait": wait_time
        }
        async with self.session.get(self.request_address, params=params) as resp:
            response = await resp.json()
            self._update_ts(response["ts"])
            return response["updates"]

    def _update_request_address(self):
        self.request_address = f"{self.server}?act=a_check"

    async def _get_long_poll_server(self):
        response = await self._make_request("groups.getLongPollServer?", {"group_id": GROUP_ID})
        response = response["response"]
        self.server = response["server"]
        self.key = response["key"]
        self.ts = response["ts"]
        self._update_request_address()

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

    async def _process_updates(self, updates: list):
        for update in updates:
            print(update)
            if update["type"] == "message_new":
                message = self._create_message(update["object"]["message"])
                _filter = self._call_filter(message)
                func = self._vk_worker.handlers.get(_filter, self._vk_worker.handlers.get("text_*"))
                if func:
                    await func(message)

    async def _start_polling(self,  wait_time: int):
        while True:
            updates = await self._get_updates(wait_time=wait_time)
            if updates:
                await self._process_updates(updates)

    async def clean_up(self):
        await self.session.close()

    async def _run_app(self, wait_time: int):
        try:
            await self._get_long_poll_server()
            await self._start_polling(wait_time=wait_time)
        finally:
            await self.clean_up()

    def run_app(self, wait_time: int = 25):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run_app(wait_time=wait_time))


if __name__ == "__main__":
    app = WebApp(bot)
    app.run_app()
