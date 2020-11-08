from config import TLG_API_KEY
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message
from tlg_bot import keyboards
from db_utils import pg_queries, redis_queries
from common_utils import dialogs, exceptions, stuff
from db_utils.models import Fight
from time import time


tlg_bot = Bot(TLG_API_KEY)
dp = Dispatcher(tlg_bot)


class StateFilter(BoundFilter):
    key = "pl_state"

    def __init__(self, pl_state: dict):
        self.pl_state = pl_state

    async def check(self, message: Message):
        player = message.conf["player"]
        state_name = list(self.pl_state.keys())[0]
        return player.states.is_that_state(state_name=state_name, value=self.pl_state[state_name])


dp.filters_factory.bind(StateFilter)


async def connect_request(message: Message):
    await message.answer(text=dialogs.req_connect, reply_markup=keyboards.connect())


async def register_request(message: Message):
    await message.answer(text=dialogs.reg_start, reply_markup=keyboards.empty_keyboard())


async def connect(message: Message, player_uuid: str):
    web_app = message.conf["web_app"]
    async with web_app.pg_pool.acquire() as connection:
        player = await web_app.get_player_from_pg(connection=connection, player_uuid=player_uuid, prefix="tlg")
        player.states.main_state = 1
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.home, reply_markup=keyboards.home())


@dp.message_handler(commands=["start"])
async def start(message: Message):
    web_app = message.conf["web_app"]
    player = message.conf["player"]
    player.states.main_state = 1
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.home, reply_markup=keyboards.home())


@dp.message_handler(pl_state={"main_state": 0})
async def register_name(message: Message):
    web_app = message.conf["web_app"]
    player = message.conf["player"]
    keyboard = None
    try:
        if len(message.text) > 30 or len(message.text) < 4:
            raise exceptions.NotCorrectName
        # if stuff.name_validation(message.text):
        #    raise exceptions.NotCorrectName
        await pg_queries.open_connection(
            pool=web_app.pg_pool, func=pg_queries.set_name_to_player,
            name=message.text, player_uuid=player.uuid)
        text = dialogs.welcome % message.text
        keyboard = keyboards.home()
        player.states.main_state = 1
        player.name = message.text
        await web_app.add_player_to_redis(player)
    except exceptions.NameAlreadyExists:
        text = dialogs.this_name_taken
    except exceptions.NotCorrectName:
        text = dialogs.name_too_long
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text=["\U0001F464 Профиль"])
async def my_profile(message: Message):
    player = message.conf["player"]
    text = dialogs.my_profile % (player.name, player.level.level, player.respect,
                                 player.level.level_max, player.power, player.health, player.mind)
    await message.answer(text=text)


@dp.message_handler(text=["\U0001F4B0 Кошелек"])
async def wallet(message: Message):
    player = message.conf["player"]
    text = dialogs.wallet % player.wallet.dollars

    await message.answer(text=text)


@dp.message_handler(text=["\U0001F4E6 Хранилище"])
async def storage(message: Message):
    player = message.conf["player"]
    text = dialogs.storage(player)
    await message.answer(text=text)


@dp.message_handler(text=["\U0001F3E0 Домой"])
async def home(message: Message):
    await message.answer(text=dialogs.home, reply_markup=keyboards.home())


@dp.message_handler(text=["\U0001F6AA На улицу", "\U00002B05 На улицу"])
async def street(message: Message):
    keyboard = keyboards.street()
    await message.answer(text=dialogs.street, reply_markup=keyboard)


@dp.message_handler(text=["\U0001F199 Прокачка", "\U00002B05 Прокачка"])
async def choose_upgrade(message: Message):
    await message.answer(text=dialogs.choose_upgrade, reply_markup=keyboards.choose_upgrade())


# ===================== Power active upgrade =====================
@dp.message_handler(text=["\U0001F4AA Сила"])
async def choose_power(message: Message):
    upgrade_block = message.conf["player"].event_stuff.upgrade_block
    if upgrade_block and (upgrade_block > int(time())):
        what_left = stuff.time_is_left(upgrade_block)
        text = dialogs.action_is_blocked % what_left
        keyboard = None
    else:
        text = dialogs.power_active_start
        keyboard = keyboards.power_active_start()
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text=["\U0001F4AA Начать"])
async def power_active_start(message: Message):
    web_app = message.conf["web_app"]
    player = message.conf["player"]
    upgrade_block = player.event_stuff.upgrade_block
    if upgrade_block and (upgrade_block > int(time())):
        what_left = stuff.time_is_left(upgrade_block)
        text = dialogs.action_is_blocked % what_left
        keyboard = None
    else:
        text = dialogs.power_active_down % 0
        keyboard = keyboards.power_active()
        player.states.main_state = 10
        player.states.upgrade_state = 0
        await web_app.add_player_to_redis(player)
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text=["\U0001f446"], pl_state={"main_state": 10})
async def power_action_up(message: Message):
    player = message.conf["player"]
    web_app = message.conf["web_app"]
    if player.states.upgrade_state % 2 != 0:
        player.states.upgrade_state += 1
        reps = player.states.upgrade_state // 2
        if reps == 10:
            text = dialogs.power_lets_finish
        else:
            text = dialogs.power_active_down % reps
        keyboard = keyboards.power_active()
    else:
        player.event_stuff.upgrade_block = int(time()) + 60  # set 60 seconds block to upgrade
        player.power = player.power - 5 if player.power > 10 else player.power
        player.states.main_state = 1
        player.states.upgrade_state = 0
        text = dialogs.power_active_stuff
        keyboard = keyboards.choose_upgrade()

    await web_app.add_player_to_redis(player)
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text=["\U0001F447"], pl_state={"main_state": 10})
async def power_action_down(message: Message):
    player = message.conf["player"]
    web_app = message.conf["web_app"]
    if player.states.upgrade_state % 2 == 0 and player.states.upgrade_state < 20:
        player.states.upgrade_state += 1
        text = dialogs.power_active_up
        keyboard = keyboards.power_active()
    elif player.states.upgrade_state == 20:
        player.health = player.health - 5 if player.health > 20 else player.health
        player.event_stuff.upgrade_block = int(time()) + 60  # set 60 seconds block to upgrade
        player.states.main_state = 1
        player.states.upgrade_state = 0
        text = dialogs.power_active_too_much
        keyboard = keyboards.choose_upgrade()
    else:
        player.health = player.health - 5 if player.health > 20 else player.health
        player.event_stuff.upgrade_block = int(time()) + 60  # set 60 seconds block to upgrade
        player.states.main_state = 1
        player.states.upgrade_state = 0
        text = dialogs.power_active_stuff
        keyboard = keyboards.choose_upgrade()

    await web_app.add_player_to_redis(player)
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text=["\U0001F44F"], pl_state={"main_state": 10})
async def power_action_stuff(message: Message):
    player = message.conf["player"]
    web_app = message.conf["web_app"]
    player.power = player.power - 5 if player.power > 5 else player.power
    player.event_stuff.upgrade_block = int(time()) + 60  # set 60 seconds block to upgrade
    player.states.main_state = 1
    player.states.upgrade_state = 0

    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.power_active_stuff, reply_markup=keyboards.choose_upgrade())


@dp.message_handler(text=["\U0000270B Поставить штангу"], pl_state={"main_state": 10})
async def power_active_stop(message: Message):
    player = message.conf["player"]
    web_app = message.conf["web_app"]
    upgrade_state = player.states.upgrade_state

    if upgrade_state < 10:  # if lower than 5 reps
        power = 0
    elif upgrade_state <= 14:  # if lower than 7 reps
        power = 5
    else:
        power = player.states.upgrade_state // 2

    if upgrade_state > 3:
        player.event_stuff.upgrade_block = int(time()) + 180  # set 3 minutes block to upgrade
    player.states.main_state = 1
    player.states.upgrade_state = 0
    player.power += power
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.power_active_stop % power, reply_markup=keyboards.choose_upgrade())


@dp.message_handler(pl_state={"main_state": 10})
async def power_active_stop(message: Message):
    await message.answer(text=dialogs.touch_buttons)


# ================= health active upgrade ================
@dp.message_handler(text=["\U00002764 Здоровье"])
async def choose_health(message: Message):
    upgrade_block = message.conf["player"].event_stuff.upgrade_block
    if upgrade_block and (upgrade_block > int(time())):
        what_left = stuff.time_is_left(upgrade_block)
        text = dialogs.action_is_blocked % what_left
        keyboard = None
    else:
        text = dialogs.health_active_start
        keyboard = keyboards.health_active_start()
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text=["\U0001F3C3 Начать"])
async def health_active_start(message: Message):
    web_app = message.conf["web_app"]
    player = message.conf["player"]
    upgrade_block = player.event_stuff.upgrade_block
    if upgrade_block and (upgrade_block > int(time())):
        what_left = stuff.time_is_left(upgrade_block)
        text = dialogs.action_is_blocked % what_left
        keyboard = None
    else:
        way, picture = stuff.gen_random_way()
        player.add_event(event_info=way)
        player.states.main_state = 11
        player.states.upgrade_state = 0
        text = dialogs.health_active_choose_way % (picture, 0)
        keyboard = keyboards.health_active()
        await web_app.add_player_to_redis(player)
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text=["\U00002B05", "\U00002B06", "\U000027A1"], pl_state={"main_state": 11})
async def health_active_turn(message: Message):
    web_app = message.conf["web_app"]
    player = message.conf["player"]
    keyboard = keyboards.choose_upgrade()
    if player.states.upgrade_state == 20:
        player.states.main_state = 1
        player.states.upgrade_state = 0
        player.health = player.health - 5 if player.health > 20 else player.health
        player.event_stuff.upgrade_block = int(time()) + 60  # set 1 minute block to upgrade
        player.clear_event_info()
        text = dialogs.health_active_too_much
    else:
        chosen_way = stuff.get_way_by_emoji(emoji_code=message.text)
        right_way = player.event_stuff.info
        if chosen_way == right_way:
            player.states.upgrade_state += 1
            way, picture = stuff.gen_random_way()
            player.add_event(event_info=way)
            if player.states.upgrade_state == 20:
                text = dialogs.health_lets_finish % (picture, 2000)
            else:
                text = dialogs.health_active_choose_way % (picture, f"{player.states.upgrade_state}00")
            keyboard = keyboards.health_active()
        else:
            text = dialogs.health_fail_way
            player.states.main_state = 1
            player.states.upgrade_state = 0
            player.event_stuff.upgrade_block = int(time()) + 60  # set 1 minute block to upgrade
            player.health = player.health - 5 if player.health > 20 else player.health
            player.clear_event_info()
    await web_app.add_player_to_redis(player)
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text=["\U0001F9B6 Остановиться"], pl_state={"main_state": 11})
async def health_active_stop(message: Message):
    web_app = message.conf["web_app"]
    player = message.conf["player"]
    distance = player.states.upgrade_state

    if distance < 10:
        new_health = 0
    elif 10 < distance < 15:
        new_health = distance - 2
    else:
        new_health = distance

    if distance > 3:
        player.event_stuff.upgrade_block = int(time()) + 180  # set 3 minutes block to upgrade
    player.health += new_health
    player.states.main_state = 1
    player.states.upgrade_state = 0
    player.clear_event_info()

    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.health_active_stop % new_health, reply_markup=keyboards.choose_upgrade())


@dp.message_handler(pl_state={"main_state": 11})
async def health_active_other(message: Message):
    await message.answer(text=dialogs.touch_buttons)


# ======================== fights ========================
@dp.message_handler(text=["\U0001F44A Разборки"])
async def fights(message: Message):
    await message.answer(text=dialogs.fight_menu, reply_markup=keyboards.fights_menu())


@dp.message_handler(text=["\U0001F50D Зарубиться"])
async def search_fight(message: Message):
    player = message.conf["player"]
    web_app = message.conf["web_app"]
    pool = web_app.redis_pool
    fight = await redis_queries.get_await_fight(pool)
    if fight:
        enemy = fight.player
        enemy.add_fight_side(enemy=player)
        player.add_fight_side(enemy=enemy)
        enemy.states.main_state = 20
        enemy.states.upgrade_state = 31
        await redis_queries.add_player(pool=pool, player=enemy)
        await stuff.send_message_to_right_platform(
            player=enemy, web_app=web_app, keyboard_name="fight_keyboard",
            text=dialogs.start_fight_enemy % (player.name, player.health)
        )
        text = dialogs.start_fight_you % (enemy.name, enemy.health)
        keyboard = keyboards.fight_keyboard()
    else:
        fight = Fight(player=player)
        await redis_queries.add_await_fight(pool=pool, fight=fight)
        text = dialogs.start_search_fight
        keyboard = keyboards.deny_search_fight()
    player.states.main_state = 20
    player.states.upgrade_state = 30

    await redis_queries.add_player(pool=pool, player=player)
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(text=["голову", "грудь", "живот", "ноги"], pl_state={"main_state": 20})
async def fight_process(message: Message):
    player = message.conf["player"]
    web_app = message.conf["web_app"]
    pool = web_app.redis_pool
    enemy = await redis_queries.get_player(pool=pool, player_uuid=player.fight_side.enemy)

    enemy_text = None
    enemy_keyboard = None

    enemy_choice = enemy.event_stuff.info
    player_choice = stuff.get_eng_hit_name(message.text)
    if enemy_choice:
        if player.states.upgrade_state == 30:  # if player is hitting
            hit_name = stuff.get_rus_hit_name(player_choice)
            hit_status, damage = stuff.calc_damage(player=player, hit_choice=player_choice, guard_choice=enemy_choice)
            enemy.fight_side.health -= damage
            enemy.states.upgrade_state = 30
            player.fight_side.damage += damage
            player.states.upgrade_state = 31
            if enemy.fight_side.health <= 0:
                text = dialogs.you_win_fight
                enemy_text = dialogs.you_lose_fight
                player.states.main_state = 1
                enemy.states.main_state = 1
                keyboard = keyboards.street()
                enemy_keyboard = "street"
            else:
                keyboard = keyboards.fight_keyboard()
                enemy_keyboard = "fight_keyboard"
                text = dialogs.get_damage_message(True, hit_status, hit_name, damage, player, enemy)
                enemy_text = dialogs.get_damage_message(False, hit_status, hit_name, damage, enemy, player)
        else:  # if player is guarding
            hit_name = stuff.get_rus_hit_name(enemy_choice)
            hit_status, damage = stuff.calc_damage(player=enemy, hit_choice=enemy_choice, guard_choice=player_choice)
            player.fight_side.health -= damage
            player.states.upgrade_state = 30
            enemy.fight_side.damage += damage
            enemy.states.upgrade_state = 31

            if player.fight_side.health <= 0:
                text = dialogs.you_lose_fight
                enemy_text = dialogs.you_lose_fight
                player.states.main_state = 1
                enemy.states.main_state = 1
                keyboard = keyboards.street()
                enemy_keyboard = "street"
            else:
                keyboard = keyboards.fight_keyboard()
                enemy_keyboard = "fight_keyboard"
                text = dialogs.get_damage_message(False, hit_status, hit_name, damage, player, enemy)
                enemy_text = dialogs.get_damage_message(False, hit_status, hit_name, damage, enemy, player)

        player.clear_event_info()
        enemy.clear_event_info()

    else:
        player.event_stuff.info = player_choice
        text = dialogs.wait_the_enemy
        keyboard = keyboards.fight_keyboard(hide_buttons=True)

    await redis_queries.add_player(pool=pool, player=enemy)
    await redis_queries.add_player(pool=pool, player=player)

    await message.answer(text=text, reply_markup=keyboard)
    if enemy_text:
        await stuff.send_message_to_right_platform(enemy, web_app, enemy_text, enemy_keyboard)


@dp.message_handler(text=["\U0001F6AB Отмена"], pl_state={"main_state": 20})
async def stop_search_fight(message: Message):
    player = message.conf["player"]
    web_app = message.conf["web_app"]
    player.states.main_state = 1
    player.states.upgrade_state = 0
    await web_app.add_player_to_redis(player)
    await redis_queries.add_await_fight(pool=web_app.redis_pool, fight=None)
    await message.answer(text=dialogs.scared, reply_markup=keyboards.street())


@dp.message_handler(text=["\U0001F4A9 Сдаться"], pl_state={"main_state": 20})
async def give_up(message: Message):
    player = message.conf["player"]
    web_app = message.conf["web_app"]
    pool = web_app.redis_pool

    enemy = await redis_queries.get_player(pool=pool, player_uuid=player.fight_side.enemy)
    enemy.states.main_state = 1
    enemy.states.upgrade_state = 0
    enemy.clear_fight_side()
    await redis_queries.add_player(pool=pool, player=enemy)
    await stuff.send_message_to_right_platform(
        player=enemy, web_app=web_app, keyboard_name="street",
        text=dialogs.enemy_give_up
    )

    player.clear_fight_side()
    player.states.main_state = 1
    player.states.upgrade_state = 0
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.you_give_up, reply_markup=keyboards.street())


@dp.message_handler(pl_state={"main_state": 20})
async def fight_other(message: Message):
    await message.answer(text=dialogs.touch_buttons)


@dp.message_handler()
async def other_messages(message: Message):
    await message.answer(text="It`s work!")
