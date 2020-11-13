import re
from aioredis import Redis
from asyncpg import Connection
from random import choice, shuffle
from time import time
from db_utils.models import Player
from db_utils import redis_queries, pg_queries
from vk_bot import keyboards as vk_keyboards
from tlg_bot import keyboards as tlg_keyboards
from typing import Optional
from loguru import logger


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
    "tlg_street": tlg_keyboards.street,
    "vk_connect": vk_keyboards.connect,
    "tlg_connect": tlg_keyboards.connect
}


async def send_message_to_right_platform(
        player: Player, web_app, text: str,
        keyboard_name: str = None,
        keyboard_args: Optional[dict] = None) -> None:
    if player.current_platform == "vk":
        keyboard = get_keyboard.get(f"vk_{keyboard_name}")
        if keyboard_name and keyboard_args:
            keyboard = keyboard(**keyboard_args)
        elif keyboard_name:
            keyboard = keyboard()
        await web_app.vk_bot.send_message(user_ids=player.vk_id, text=text, keyboard=keyboard)
    else:
        bot = web_app.tlg_dp.bot
        keyboard = get_keyboard.get(f"tlg_{keyboard_name}")
        if keyboard_name and keyboard_args:
            keyboard = keyboard(**keyboard_args)
        elif keyboard_name:
            keyboard = keyboard()
        await bot.send_message(chat_id=player.tlg_id, text=text, reply_markup=keyboard)


def calc_damage(player: Player, hit_choice: str, guard_choice: str) -> tuple:
    ratio = {
        "head": 1,
        "chest": 0.75,
        "abdomen": 0.8,
        "legs": 0.5
    }
    if hit_choice == guard_choice:
        damage_ratio = 0.1
        hit_status = False
    else:
        damage_ratio = ratio[hit_choice]
        hit_status = True
    damage = int(player.power * damage_ratio)

    return hit_status, damage


def get_rus_hit_name(hit_name: str) -> str:
    translate = {
        "head": "голову",
        "chest": "грудь",
        "abdomen": "живот",
        "legs": "ноги"
    }
    return translate[hit_name]


def get_eng_hit_name(hit_name: str) -> str:
    translate = {
        "голову": "head",
        "грудь": "chest",
        "живот": "abdomen",
        "ноги": "legs"
    }
    return translate[hit_name]


def close_fight(winner: Player, loser: Player):
    logger.debug(f"{type(winner)}")
    for player in (winner, loser):
        logger.debug(f"{type(player)}")
        player.states.main_state = 1
        player.states.upgrade_state = 0
        player.clear_event_info()
        player.clear_fight_side()


def create_event(event_name: str, player: Player) -> dict:
    return {"event_name": event_name, "player": player.serialize()}


async def check_dependencies(redis: Redis, player: Player) -> list:
    events = []
    if player.fight_side:
        enemy = player.fight_side.enemy
        close_fight(winner=enemy, loser=player)
        event = create_event(event_name="enemy_give_up", player=enemy)
        events.append(event)
        await redis_queries.add_player(pool=redis, player=enemy)

    return events


async def disconnect_player(pg_conn: Connection, redis: Redis, player: Player) -> list:
    events = await check_dependencies(redis=redis, player=player)
    await redis_queries.remove_player(pool=redis, player=player)
    await pg_queries.update_player(connection=pg_conn, player=player)

    return events
