from vk_api.vk import Keyboard, Button
from db_utils.models import Levels


def main_menu() -> Keyboard:
    keyboard = Keyboard()
    keyboard.add_button(Button(label="Тут будет меню"))
    return keyboard


def connect() -> Keyboard:
    keyboard = Keyboard()
    keyboard.add_button(Button(label="Подключиться", payload={"command": "connect"}, color="positive"))
    return keyboard


def empty_keyboard() -> Keyboard:
    keyboard = Keyboard()
    return keyboard


def payload_start() -> Keyboard:
    keyboard = Keyboard()
    keyboard.add_button(Button(label="start button", payload={"command": "start"}))
    return keyboard


def info_payload() -> Keyboard:
    keyboard = Keyboard(inline=True)
    keyboard.add_button(Button(label="send info", payload={"info": "one two three"}))
    return keyboard


def home() -> Keyboard:
    keyboard = Keyboard()
    keyboard.add_button(Button(label="\U0001F464 Профиль", payload={"command": "my_profile"}))
    keyboard.add_button(Button(label="\U0001F4E6 Хранилище", payload={"command": "storage"}))
    keyboard.add_button(Button(label="\U0001F4B0 Кошелек", payload={"command": "wallet"}))

    keyboard.add_empty_row()
    keyboard.add_button(Button(label="\U0001F6AA На улицу", payload={"command": "street"}, color="primary"))
    keyboard.add_button(Button(label="\U00002699 Настройки", payload={"command": "settings"}, color="primary"))

    return keyboard


def street(level: Levels) -> Keyboard:
    keyboard = Keyboard()
    keyboard.add_button(Button(label="\U0001F919 Движухи", payload={"command": "job"}))
    keyboard.add_button(Button(label="\U0001F199 Прокачка", payload={"command": "upgrade"}))
    keyboard.add_empty_row()

    keyboard.add_button(Button(label="\U0001F4B0 Барыга", payload={"command": "seller"}))

    if level.level < 3:
        keyboard.add_button(Button(label="\U0001F44A Разборки", payload={"command": "lock 3"}))
    else:
        keyboard.add_button(Button(label="\U0001F512 Разборки", payload={"command": "fights"}))

    keyboard.add_empty_row()
    keyboard.add_button(Button(label="\U0001F3E0 Домой", payload={"command": "home"}, color="primary"))
    keyboard.add_button(Button(label="\U0001F5FA Карта", payload={"command": "map"}, color="primary"))
    keyboard.add_button(Button(label="\U00002699 Настройки", payload={"command": "settings"}, color="primary"))

    return keyboard
