import re
from random import choice, shuffle
from time import time


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
        left_str = f"{days}:{hours - days * 24}:{minutes - hours * 60}:{seconds - minutes * 60}"
    elif hours:
        left_str = f"{hours}:{minutes - hours * 60}:{seconds - minutes * 60}"
    elif minutes:
        left_str = f"{minutes}:{seconds - minutes * 60}"
    else:
        left_str = f"{seconds} сек."

    return left_str
