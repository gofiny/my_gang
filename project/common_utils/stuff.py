import re
from random import choice, shuffle


def name_validation(text):
    pattern = r'[^\w\s]'
    if re.search(pattern, text):
        #  valid_name = re.sub(pattern, '_', text)
        return False
    return True


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
