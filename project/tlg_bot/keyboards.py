from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from random import shuffle


def main_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("Здесь будет меню"))
    return keyboard


def connect() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("Подключиться"))
    return keyboard


def empty_keyboard() -> ReplyKeyboardRemove:
    keyboard = ReplyKeyboardRemove()
    return keyboard


def home() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        KeyboardButton("\U0001F464 Профиль"),
        KeyboardButton("\U0001F4E6 Хранилище"),
        KeyboardButton("\U0001F4B0 Кошелек")
    )
    keyboard.row(
        KeyboardButton("\U0001F6AA На улицу"),
        KeyboardButton("\U00002699 Настройки")
    )
    return keyboard


def street():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        KeyboardButton("\U0001F919 Движухи"),
        KeyboardButton("\U0001F199 Прокачка")
    )
    keyboard.row(
        KeyboardButton("\U0001F575 Барыга"),
        KeyboardButton("\U0001F44A Разборки")
    )
    keyboard.row(
        KeyboardButton("\U0001F3E0 Домой"),
        KeyboardButton("\U0001F5FA Карта"),
        KeyboardButton("\U00002699 Настройки")
    )
    return keyboard


def choose_upgrade():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row(KeyboardButton("\U0001F4AA Сила"))
    keyboard.row(KeyboardButton("\U00002764 Здоровье"))
    keyboard.row(KeyboardButton("\U0001F9E0 Интеллект"))
    keyboard.row(KeyboardButton("\U00002B05 На улицу"))

    return keyboard


def power_active_start():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("\U0001F4AA Начать"))
    keyboard.row(KeyboardButton("\U00002B05 Прокачка"))

    return keyboard


def power_active():
    keyboard = ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
    up = KeyboardButton("\U0001f446")
    down = KeyboardButton("\U0001F447")
    other_buttons = [KeyboardButton("\U0001F44F")] * 6
    buttons = [*other_buttons, up, down]
    shuffle(buttons)
    keyboard.add(*buttons)
    keyboard.add(KeyboardButton("\U0000270B Поставить штангу"))
    return keyboard


def health_active_start():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("\U0001F3C3 Начать"))
    keyboard.row(KeyboardButton("\U00002B05 Прокачка"))

    return keyboard


def health_active():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    keyboard.add(
        KeyboardButton("\U00002B05"),
        KeyboardButton("\U00002B06"),
        KeyboardButton("\U000027A1"),
        KeyboardButton("\U0001F9B6 Остановиться")
    )

    return keyboard


def fights_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton("\U0001F50D Зарубиться"),
        KeyboardButton("\U00002B05 На улицу")
    )
    return keyboard


def deny_search_fight():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("\U0001F6AB Отмена"))
    return keyboard


def fight_keyboard(hide_buttons: bool = False):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton("голову"),
        KeyboardButton("грудь"),
        KeyboardButton("живот"),
        KeyboardButton("ноги")
    ]
    if not hide_buttons:
        keyboard.add(*buttons)

    keyboard.add(
        KeyboardButton("\U0001F4A9 Сдаться")
    )
    return keyboard
