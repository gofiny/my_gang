from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from db_utils.models import Levels


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


def street(level: Levels):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        KeyboardButton("\U0001F919 Движухи"),
        KeyboardButton("\U0001F199 Прокачка")
    )
    keyboard.row(
        KeyboardButton("\U0001F4B0 Барыга"),
        KeyboardButton("\U0001F44A Разборки") if level.level > 3 else KeyboardButton("\U0001F4B0 Разборки")
    )
    keyboard.row(
        KeyboardButton("\U0001F3E0 Домой"),
        KeyboardButton("\U0001F5FA Карта"),
        KeyboardButton("\U00002699 Настройки")
    )
    return keyboard
