from vk_api.vk import Keyboard, Button


def subscribe() -> Keyboard:
    keyboard = Keyboard()
    keyboard.add_button(Button(label="Новости", color="primary"))
    keyboard.add_empty_row()
    keyboard.add_button(Button(label="Подписаться на рассылку", payload={"command": "subscribe"}, color="positive"))
    return keyboard


def unsubscribe() -> Keyboard:
    keyboard = Keyboard()
    keyboard.add_button(Button(label="Новости", color="primary"))
    keyboard.add_empty_row()
    keyboard.add_button(Button(label="Отписаться от рассылки", payload={"command": "unsubscribe"}, color="negative"))
    return keyboard


def telegram_link() -> Keyboard:
    keyboard = Keyboard(inline=True)
    keyboard.add_button(Button(b_type="open_link", label="Перейти в наш telegram канал", link="https://t.me/MyGangNews"))
    return keyboard
