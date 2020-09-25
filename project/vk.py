from aiohttp import ClientSession
from typing import Union, Optional, List
from random import getrandbits, choice


class Message:
    def __init__(self, message_json: dict):
        self.id = message_json["id"]
        self.date = message_json["date"]
        self.from_id = message_json["from_id"]
        self.text = message_json.get("payload")
        self.payload = message_json.get("payload")


class Button:
    def __init__(self, b_type: str, color: str = "secondary", **kwargs):
        self.button = {"action": {"type": b_type}}
        params = {**kwargs}
        self.button["type"]["label"] = params["label"]
        if params.get("payload"):
            self.button["type"]["payload"] = params["payload"]

        if b_type == "text" or b_type == "callback":
            self.button["color"] = color
        elif b_type == "open_link":
            self.button["type"]["link"] = params["link"]
        else:
            raise TypeError(f"Button type {b_type} is not support")


class Keyboard:
    def __init__(self, one_time: bool, inline: bool):
        self.one_time = one_time
        self.inline = inline


class VK:
    def __init__(self, api_key, api_ver):
        self._session = ClientSession()
        self.handlers = {}
        self._API_KEY = api_key
        self._API_VER = api_ver

    def _make_filter(self, **params):
        params = {**params}
        if params.get("text") and params.get("payload"):
            pass

    def _register_handler(self, func, **kwargs):
        filters = {**kwargs}
        self.handlers[text] = func

    def message_handler(self, text: Optional[str] = None, payload: Optional[str] = None):
        def decorator(func):
            self._register_handler(text, func)
        return decorator

    @staticmethod
    def _get_random_id() -> int:
        return getrandbits(31) * choice([-1, 1])

    async def clean_up(self):
        await self._session.close()

    async def _make_request(self, method_name: str, params: dict) -> None:
        _BASE_URL = "https://api.vk.com/method/%s"
        params = {
            **params,
            "access_token": self._API_KEY,
            "v": self._API_VER
        }
        async with self._session.get(_BASE_URL % method_name, params=params) as resp:
            if resp.status != 200:
                print(await resp.text())

    async def send_message(self, user_ids: Union[List[int], int],
                           text: str, attachment: Optional[str] = None,
                           payload: Optional[str] = None) -> None:
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
