from aiohttp import ClientSession
from typing import Union, Optional, List
from random import getrandbits, choice
from .config import API_KEY, API_VER


class VK:
    def __init__(self):
        self.session = ClientSession()

    @staticmethod
    def _get_random_id() -> int:
        return getrandbits(31) * choice([-1, 1])

    async def clean_up(self):
        await self.session.close()

    async def _make_request(self, method_name: str, params: dict) -> None:
        _BASE_URL = "https://api.vk.com/method/%s"
        params = {
            **params,
            "access_token": API_KEY,
            "v": API_VER
        }
        async with self.session.get(_BASE_URL % method_name, params=params) as resp:
            if resp.status != 200:
                print(await resp.text())

    async def send_message(self, user_ids: Union[List[int], int],
                           text: str, attachment: Optional[str],
                           payload: str) -> None:
        if isinstance(user_ids, list):
            user_ids = ", ".join(map(str, user_ids))

        params = {
            "user_ids": user_ids,
            "random_id": self._get_random_id(),
            "message": text
        }

        if attachment:
            params["attachment"] = attachment

        if payload:
            params["payload"] = payload

        await self._make_request(method_name="messages.send?", params=params)
