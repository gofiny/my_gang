from vk import Keyboard, Button


def payload_start():
    keyboard = Keyboard()
    keyboard.add_button(Button(label="start button", payload={"command": "start"}))
    return keyboard


def info_payload():
    keyboard = Keyboard()
    keyboard.add_button(Button(label="send info", payload={"info": "one two three"}))
    return keyboard
