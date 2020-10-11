from aiohttp import ClientSession
from db_utils.models import Player
from typing import Union, Optional, List, Callable
from random import getrandbits, choice
from typing import Optional
from applications.web_app import WebApp
import json


class Message:
    def __init__(self, message_json: dict, bot: "VK", web_app: WebApp, player: Optional[Player]):
        self.id = message_json["id"]
        self.date = message_json["date"]
        self.from_id = message_json["from_id"]
        self.text = message_json.get("text")
        self.payload = message_json.get("payload")
        self.bot = bot
        self.player = player
        self.web_app = web_app

        if self.payload:
            self.payload = json.loads(self.payload)

    async def answer(self, text: str, attachment: Optional[str] = None,
                     payload: Optional[str] = None,
                     keyboard: Optional["Keyboard"] = None) -> None:
        await self.bot.send_message(
            user_ids=self.from_id, text=text,
            attachment=attachment, payload=payload,
            keyboard=keyboard
        )


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
        self._session = None
        self.handlers = {}  # {"text_some_text": {"states": {None: func}}}}
        self._API_KEY = api_key
        self._API_VER = api_ver

    @staticmethod
    def get_new_session():
        return ClientSession()

    @property
    def session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = self.get_new_session()
        return self._session

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

    @staticmethod
    def _create_state_filter(func: Callable, state: Optional[dict]) -> dict:
        _state = {
            "states": {
                json.dumps(state): func
            }
        }
        return _state

    def add_state_to_filter(self, _filter: str, _requirement_state: dict, _state: dict, func: Callable) -> dict:
        exists_filter = self.handlers.get(_filter)
        if exists_filter:
            exists_filter["states"][json.dumps(_requirement_state)] = func
            return exists_filter
        return _state

    def _register_handler(
            self, func: Callable, text: Optional[str] = None,
            payload: Optional[dict] = None,
            state: Optional[dict] = None) -> None:
        _filter = self._make_filter(text=text, payload=payload)
        _state = self._create_state_filter(func=func, state=state)
        finished_filter = self.add_state_to_filter(_filter=_filter, _requirement_state=state, _state=_state, func=func)
        self.handlers[_filter] = finished_filter

    def message_handler(self, text: Optional[str] = None,
                        payload: Optional[dict] = None,
                        state: Optional[dict] = None) -> Callable:
        def decorator(func):
            self._register_handler(func, text, payload, state)
        return decorator

    @staticmethod
    def _get_random_id() -> int:
        return getrandbits(31) * choice([-1, 1])

    async def clean_up(self) -> None:
        await self.session.close()

    async def _make_request(self, method_name: str, params: dict) -> None:
        _BASE_URL = "https://api.vk.com/method/%s"
        params = {
            **params,
            "access_token": self._API_KEY,
            "v": self._API_VER
        }
        async with self.session.get(_BASE_URL % method_name, params=params) as resp:
            # if resp.status != 200:
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
