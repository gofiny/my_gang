from aiohttp import ClientSession
from typing import Union, Optional, List, Callable
from random import getrandbits, choice
import json


class Message:
    def __init__(self, message_json: dict):
        self.id = message_json["id"]
        self.date = message_json["date"]
        self.from_id = message_json["from_id"]
        self.text = message_json.get("text")
        self.payload = message_json.get("payload")
        if self.payload:
            self.payload = json.loads(self.payload)


class Button:
    def __init__(self, b_type: str = "text", color: str = "secondary", **kwargs):
        self.button = {"action": {"type": b_type}}
        params = {**kwargs}
        self.button["action"]["label"] = params["label"]
        if params.get("payload"):
            self.button["action"]["payload"] = params["payload"]

        if b_type == "text" or b_type == "callback":
            self.button["color"] = color
        elif b_type == "open_link":
            self.button["action"]["link"] = params["link"]
        else:
            raise TypeError(f"Button type {b_type} is not support")


class Keyboard:
    def __init__(self, one_time: bool = False, inline: bool = False):
        self.one_time = one_time
        self.inline = inline
        self.buttons = []

    def add_empty_row(self):
        self.buttons.append([])

    def add_buttons_row(self, buttons: List[Button]):
        self.buttons.append([_button.button for _button in buttons])

    def add_button(self, button: Button):
        try:
            if len(self.buttons[-1]) == 5:
                self.add_empty_row()
        except IndexError:
            self.add_empty_row()
        self.buttons[-1].append(button.button)

    def get_keyboard(self):
        _keyboard = {
            "one_time": self.one_time,
            "inline": self.inline,
            "buttons": self.buttons
        }
        return json.dumps(_keyboard)


class VK:
    def __init__(self, api_key, api_ver):
        self._session = ClientSession()
        self.handlers = {}  # {"text_some_text": func} or {"payload_payload_command": func}
        self._API_KEY = api_key
        self._API_VER = api_ver

    @staticmethod
    def _make_filter(**params) -> str:
        params = {**params}
        _filter = ""
        text = params.get("text")
        payload = params.get("payload")
        if payload:
            if payload.get("command"):
                _filter = f'payload_{payload["command"]}'
            elif payload.get("info"):
                _filter = f'text_{text}'
        elif text:
            _filter = f'text_{text}'

        return _filter

    def _register_handler(self, func, text: Optional[str] = None, payload: Optional[dict] = None) -> None:
        _filter = self._make_filter(text=text, payload=payload)
        self.handlers[_filter] = func

    def message_handler(self, text: Optional[str] = None, payload: Optional[dict] = None) -> Callable:
        def decorator(func):
            self._register_handler(func, text, payload)
        return decorator

    @staticmethod
    def _get_random_id() -> int:
        return getrandbits(31) * choice([-1, 1])

    async def clean_up(self) -> None:
        await self._session.close()

    async def _make_request(self, method_name: str, params: dict) -> None:
        _BASE_URL = "https://api.vk.com/method/%s"
        params = {
            **params,
            "access_token": self._API_KEY,
            "v": self._API_VER
        }
        async with self._session.get(_BASE_URL % method_name, params=params) as resp:
            #if resp.status != 200:
            print(await resp.text())

    async def send_message(self, user_ids: Union[List[int], int],
                           text: str, attachment: Optional[str] = None,
                           payload: Optional[str] = None,
                           keyboard: Optional[Keyboard] = None) -> None:
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

        if keyboard:
            params["keyboard"] = keyboard.get_keyboard()

        await self._make_request(method_name="messages.send?", params=params)
