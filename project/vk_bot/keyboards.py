from vk_api.vk import Keyboard, Button
from db_utils.models import Levels
from random import shuffle


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
    keyboard.add_button(Button(label="\U0001F199 Прокачка", payload={"command": "choose_upgrade"}))
    keyboard.add_empty_row()

    keyboard.add_button(Button(label="\U0001F575 Барыга", payload={"command": "seller"}))

    if level.level < 3:
        keyboard.add_button(Button(label="\U0001F44A Разборки", payload={"command": "lock 3"}))
    else:
        keyboard.add_button(Button(label="\U0001F44A Разборки", payload={"command": "fights"}))

    keyboard.add_empty_row()
    keyboard.add_button(Button(label="\U0001F3E0 Домой", payload={"command": "home"}, color="primary"))
    keyboard.add_button(Button(label="\U0001F5FA Карта", payload={"command": "map"}, color="primary"))
    keyboard.add_button(Button(label="\U00002699 Настройки", payload={"command": "settings"}, color="primary"))

    return keyboard


def choose_upgrade():
    keyboard = Keyboard()
    keyboard.add_button(Button(label="\U0001F4AA Сила", payload={"command": "choose_power"}))

    keyboard.add_empty_row()
    keyboard.add_button(Button(label="\U00002764 Здоровье", payload={"command": "choose_health"}))

    keyboard.add_empty_row()
    keyboard.add_button(Button(label="\U0001F9E0 Интеллект", payload={"command": "choose_mind"}))

    keyboard.add_empty_row()
    keyboard.add_button(Button(label="\U00002B05 Назад", payload={"command": "street"}, color="primary"))

    return keyboard


def power_active_start():
    keyboard = Keyboard()
    keyboard.add_button(Button(label="\U0001F4AA Начать", payload={"command": "power_active_start"}, color="positive"))

    keyboard.add_empty_row()
    keyboard.add_button(Button(label="\U00002B05 Назад", payload={"command": "choose_upgrade"}, color="primary"))

    return keyboard


def power_active():
    keyboard = Keyboard(one_time=True, default_width=4)
    up = Button(label="\U0001f446", payload={"command": "power_action_up"})
    down = Button(label="\U0001F447", payload={"command": "power_action_down"})
    other_buttons = [Button(label="\U0001F44F", payload={"command": "power_action_stuff"})] * 6
    buttons = [*other_buttons, up, down]
    shuffle(buttons)
    keyboard.add_buttons(buttons=buttons)
    keyboard.add_button(Button(label="\U0000270B Поставить штангу",
                               payload={"command": "power_active_stop"},
                               color="primary"))
    return keyboard
