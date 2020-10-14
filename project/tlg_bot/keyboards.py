from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


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
