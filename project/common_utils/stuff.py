import re
from random import choice, shuffle
from time import time
from db_utils.models import Player
from applications.web_app import WebApp
from vk_bot import keyboards as vk_keyboards
from tlg_bot import keyboards as tlg_keyboards


def name_validation(text):
    pattern = r'[^\w\s]'
    if re.search(pattern, text):
        #  valid_name = re.sub(pattern, '_', text)
        return False
    return True


def get_way_by_emoji(emoji_code: str) -> str:
    way = {
        "\U00002B05": "left",
        "\U000027A1": "right",
        "\U00002B06": "straight"
    }
    return way[emoji_code]


def get_random_picture() -> str:
    pictures = [
        "left_cops_band",
        "left_band_cops",
        "cops_straight_band",
        "band_straight_cops",
        "cops_band_right",
        "band_cops_right"
    ]
    shuffle(pictures)
    return choice(pictures)


def gen_random_way() -> tuple:
    picture = get_random_picture()
    elements = picture.split("_")
    way = None
    for element in elements:
        if element in {"left", "right", "straight"}:
            way = element
    return way, picture


def time_is_left(block_time: int) -> str:
    seconds = block_time - int(time())
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    if days:
        left_str = f"{days} дн. {hours - days * 24} час. {minutes - hours * 60} мин. {seconds - minutes * 60} сек."
    elif hours:
        left_str = f"{hours} час. {minutes - hours * 60} мин. {seconds - minutes * 60} сек."
    elif minutes:
        left_str = f"{minutes} мин. {seconds - minutes * 60} сек."
    else:
        left_str = f"{seconds} сек."

    return left_str


get_keyboard = {
    "vk_fight_keyboard": vk_keyboards.fight_keyboard,
    "tlg_fight_keyboard": tlg_keyboards.fight_keyboard,
    "vk_street": vk_keyboards.street,
    "tlg_street": tlg_keyboards.street
}


async def send_message_to_right_platform(player: Player, web_app: WebApp, text: str, keyboard_name: str = None) -> None:
    if player.current_platform == "vk":
        keyboard = get_keyboard[f"vk_{keyboard_name}"]() if keyboard_name else None
        await web_app.vk_bot.send_message(user_ids=player.vk_id, text=text, keyboard=keyboard)
    else:
        bot = web_app.tlg_dp.bot
        keyboard = get_keyboard[f"tlg_{keyboard_name}"]() if keyboard_name else None
        await bot.send_message(chat_id=player.tlg_id, text=text, reply_markup=keyboard)
