import asyncio
from aiohttp import ClientSession
from config import DEBUG_API_KEY, API_VER, DEBUG_GROUP_ID
from typing import Optional


class WebApp:
    def __init__(self):
        self.session = ClientSession()
        self.ts = ""
        self.server = ""
        self.key = ""
        self.request_address = ""

    async def _make_request(self, method_name: str, params: dict) -> Optional[dict]:
        _BASE_URL = "https://api.vk.com/method/%s"
        params = {
            **params,
            "access_token": DEBUG_API_KEY,
            "v": API_VER
        }
        async with self.session.get(_BASE_URL % method_name, params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                print(await resp.text())

    async def _update_ts(self, new_ts):
        self.ts = new_ts

    async def _get_updates(self) -> list:
        params = {
            "ts": self.ts,
            "key": self.key,
            "wait": 25
        }
        async with self.session.get(self.request_address, params=params) as resp:
            response = await resp.json()
            print(response)
            print(self.key)
            #await self._update_ts(response["ts"])
            #return response["updates"]

    async def _update_request_address(self):
        self.request_address = f"{self.server}?act_a_check"

    async def _get_long_poll_server(self):
        response = await self._make_request("groups.getLongPollServer?", {"group_id": DEBUG_GROUP_ID})
        response = response["response"]
        self.server = response["server"]
        self.key = response["key"]
        self.ts = response["ts"]
        print(self.key)
        await self._update_request_address()


    async def set_long_poll(self):
        params = {
            "key": self.key,
            "ts": self.ts,
            "wait": 25
        }

    async def clean_up(self):
        await self.session.close()

    async def test(self):
        try:
            await self._get_long_poll_server()
            updates = await self._get_updates()
            print(updates)
        finally:
            await self.clean_up()

    def run_app(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.test())


if __name__ == "__main__":
    app = WebApp()
    app.run_app()
