from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("Здесь будет меню"))
    return keyboard


def connect() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("Подключиться"))
    return keyboard


def empty_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup()
    return keyboard
