from vk_api.vk import Keyboard, Button


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

