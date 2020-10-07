from vk_api.vk import Keyboard, Button


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


def test_count_buttons(button_count: int) -> Keyboard:
    keyboard = Keyboard()
    for num, button in enumerate(range(1, button_count)):
        keyboard.add_button(Button(label=num))

    return keyboard
