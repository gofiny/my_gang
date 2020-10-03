from vk_api.vk import Keyboard, Button


def subscribe() -> Keyboard:
    keyboard = Keyboard()
    keyboard.add_button(Button(label="Подписаться на рассылку", payload={"command": "subscribe"}))
    return keyboard


def unsubscribe() -> Keyboard:
    keyboard = Keyboard()
    keyboard.add_button(Button(label="Отписаться от рассылки", payload={"command": "unsubscribe"}))
    return keyboard
