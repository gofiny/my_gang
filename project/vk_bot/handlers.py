from vk_api.vk import Message, VK
from config import VK_API_KEY, VK_API_VER
from vk_bot import keyboards
from common_utils import dialogs, exceptions, stuff
from db_utils import pg_queries, redis_queries
from db_utils.models import Fight
from loguru import logger
from time import time


vk_bot = VK(VK_API_KEY, VK_API_VER)


async def connect_request(message: Message):
    await message.answer(text=dialogs.req_connect, keyboard=keyboards.connect())


async def register_request(message: Message):
    await message.answer(text=dialogs.reg_start, keyboard=keyboards.empty_keyboard())


async def connect(message: Message, player_uuid: str):
    web_app = message.web_app
    async with web_app.pg_pool.acquire() as connection:
        player = await web_app.get_player_from_pg(connection=connection, player_uuid=player_uuid)
        player.states.main_state = 1
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.home, keyboard=keyboards.home())


@vk_bot.message_handler(payload={"command": "start"})
async def start(message: Message):
    web_app = message.web_app
    player = message.player
    player.states.main_state = 1
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.home, keyboard=keyboards.main_menu())


@vk_bot.message_handler(text="*", state={"main_state": 0})
async def register_name(message: Message):
    web_app = message.web_app
    player = message.player
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
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "my_profile"})
async def my_profile(message: Message):
    player = message.player
    web_app = message.web_app
    text = dialogs.my_profile % (player.name, player.level.level, player.respect,
                                 player.level.level_max, player.power, player.health, player.mind)
    await redis_queries.add_player(pool=web_app.redis_pool, player=player)
    await message.answer(text=text)


@vk_bot.message_handler(payload={"command": "wallet"})
async def wallet(message: Message):
    player = message.player
    web_app = message.web_app
    text = dialogs.wallet % player.wallet.dollars

    await redis_queries.add_player(pool=web_app.redis_pool, player=player)
    await message.answer(text=text)


@vk_bot.message_handler(payload={"command": "storage"})
async def storage(message: Message):
    player = message.player
    web_app = message.web_app
    text = dialogs.storage(player)

    await redis_queries.add_player(pool=web_app.redis_pool, player=player)
    await message.answer(text=text)


@vk_bot.message_handler(payload={"command": "home"})
async def home(message: Message):
    player = message.player
    web_app = message.web_app
    await redis_queries.add_player(pool=web_app.redis_pool, player=player)
    await message.answer(text=dialogs.home, keyboard=keyboards.home())


@vk_bot.message_handler(payload={"command": "street"})
async def street(message: Message):
    player = message.player
    web_app = message.web_app
    await redis_queries.add_player(pool=web_app.redis_pool, player=player)
    await message.answer(text=dialogs.street, keyboard=keyboards.street())


@vk_bot.message_handler(payload={"command": "choose_upgrade"})
async def choose_upgrade(message: Message):
    player = message.player
    web_app = message.web_app
    await redis_queries.add_player(pool=web_app.redis_pool, player=player)
    await message.answer(text=dialogs.choose_upgrade, keyboard=keyboards.choose_upgrade())


# ===================== Power active upgrade =====================
@vk_bot.message_handler(payload={"command": "choose_power"})
async def choose_power(message: Message):
    web_app = message.web_app
    player = message.player
    upgrade_block = player.event_stuff.upgrade_block
    if upgrade_block and (upgrade_block > int(time())):
        what_left = stuff.time_is_left(upgrade_block)
        text = dialogs.action_is_blocked % what_left
        keyboard = None
    else:
        text = dialogs.power_active_start
        keyboard = keyboards.power_active_start()

    await redis_queries.add_player(pool=web_app.redis_pool, player=player)
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "power_active_start"})
async def power_active_start(message: Message):
    web_app = message.web_app
    player = message.player
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
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "power_action_up"}, state={"main_state": 10})
async def power_action_up(message: Message):
    player = message.player
    if player.states.upgrade_state % 2 != 0:
        player.states.upgrade_state += 1
        reps = player.states.upgrade_state // 2
        if reps == 10:
            text = dialogs.power_lets_finish
        else:
            text = dialogs.power_active_down % reps
        keyboard = keyboards.power_active()
    else:
        player.states.main_state = 1
        player.states.upgrade_state = 0
        player.event_stuff.upgrade_block = int(time()) + 60  # set 60 seconds block to upgrade
        player.power = player.power - 5 if player.power > 10 else player.power
        text = dialogs.power_active_stuff
        keyboard = keyboards.choose_upgrade()

    await message.web_app.add_player_to_redis(player)
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "power_action_down"}, state={"main_state": 10})
async def power_action_down(message: Message):
    player = message.player
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
        player.states.main_state = 1
        player.states.upgrade_state = 0
        player.health = player.health - 5 if player.health > 20 else player.health
        player.event_stuff.upgrade_block = int(time()) + 60  # set 60 seconds block to upgrade
        text = dialogs.power_active_stuff
        keyboard = keyboards.choose_upgrade()

    await message.web_app.add_player_to_redis(player)
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "power_action_stuff"}, state={"main_state": 10})
async def power_action_stuff(message: Message):
    player = message.player
    player.power = player.power - 5 if player.power > 5 else player.power
    player.event_stuff.upgrade_block = int(time()) + 60  # set 60 seconds block to upgrade
    player.states.main_state = 1
    player.states.upgrade_state = 0

    await message.web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.power_active_stuff, keyboard=keyboards.choose_upgrade())


@vk_bot.message_handler(payload={"command": "power_active_stop"}, state={"main_state": 10})
async def power_active_stop(message: Message):
    player = message.player
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
    await message.web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.power_active_stop % power, keyboard=keyboards.choose_upgrade())


@vk_bot.message_handler(text="*", state={"main_state": 10})
async def power_active_other(message: Message):
    await message.answer(text=dialogs.touch_buttons)


# ================= health active upgrade ================
@vk_bot.message_handler(payload={"command": "choose_health"})
async def choose_health(message: Message):
    web_app = message.web_app
    player = message.player
    upgrade_block = player.event_stuff.upgrade_block
    if upgrade_block and (upgrade_block > int(time())):
        what_left = stuff.time_is_left(upgrade_block)
        text = dialogs.action_is_blocked % what_left
        keyboard = None
    else:
        text = dialogs.health_active_start
        keyboard = keyboards.health_active_start()

    await web_app.add_player_to_redis(player)
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "health_active_start"})
async def health_active_start(message: Message):
    web_app = message.web_app
    player = message.player
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
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "health_turn"})
async def health_active_turn(message: Message):
    web_app = message.web_app
    player = message.player
    keyboard = keyboards.choose_upgrade()
    if player.states.upgrade_state == 20:
        player.states.main_state = 1
        player.states.upgrade_state = 0
        player.health = player.health - 5 if player.health > 20 else player.health
        player.event_stuff.upgrade_block = int(time()) + 60  # set 1 minute block to upgrade
        player.clear_event_info()
        text = dialogs.health_active_too_much
    else:
        chosen_way = message.payload["command"].split()[1]
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
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "health_active_stop"}, state={"main_state": 11})
async def health_active_stop(message: Message):
    web_app = message.web_app
    player = message.player
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
    await message.answer(text=dialogs.health_active_stop % new_health, keyboard=keyboards.choose_upgrade())


@vk_bot.message_handler(text="*", state={"main_state": 11})
async def health_active_other(message: Message):
    await message.answer(text=dialogs.touch_buttons)


# ================= fights ================
@vk_bot.message_handler(payload={"command": "fights"})
async def fights(message: Message):
    web_app = message.web_app
    player = message.player
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.fight_menu, keyboard=keyboards.fights_menu())


@vk_bot.message_handler(payload={"command": "search_fight"})
async def search_fight(message: Message):
    player = message.player
    web_app = message.web_app
    pool = web_app.redis_pool

    fight = await redis_queries.get_await_fight(pool)
    if fight:
        enemy = fight.player
        enemy.add_fight_side(enemy=player)
        player.add_fight_side(enemy=enemy)
        player.states.main_state = 20
        player.states.upgrade_state = 31
        await redis_queries.add_player(pool=pool, player=enemy)
        await stuff.send_message_to_right_platform(
            player=enemy, web_app=web_app, keyboard_name="fight_keyboard",
            text=dialogs.start_fight_you % (player.name, player.health)
        )
        text = dialogs.start_fight_enemy % (enemy.name, enemy.health)
        keyboard = keyboards.fight_keyboard()
    else:
        player.states.main_state = 20
        player.states.upgrade_state = 30
        fight = Fight(player=player)
        await redis_queries.add_await_fight(pool=pool, fight=fight)
        text = dialogs.start_search_fight
        keyboard = keyboards.deny_search_fight()

    await redis_queries.add_player(pool=pool, player=player)
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "fight"}, state={"main_state": 20})
async def fight_process(message: Message):
    player = message.player
    web_app = message.web_app
    pool = web_app.redis_pool
    enemy = await redis_queries.get_player(pool=pool, player_uuid=player.fight_side.enemy)

    enemy_text = None
    enemy_keyboard = None

    enemy_choice = enemy.event_stuff.info
    player_choice = message.payload["command"].split()[1]
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
                text += dialogs.choice_guard
                enemy_text = dialogs.get_damage_message(False, hit_status, hit_name, damage, enemy, player)
                enemy_text += dialogs.choice_hit
        else:  # if player is guarding
            hit_name = stuff.get_rus_hit_name(enemy_choice)
            hit_status, damage = stuff.calc_damage(player=enemy, hit_choice=enemy_choice, guard_choice=player_choice)
            player.fight_side.health -= damage
            player.states.upgrade_state = 30
            enemy.fight_side.damage += damage
            enemy.states.upgrade_state = 31

            if player.fight_side.health <= 0:
                text = dialogs.you_lose_fight
                enemy_text = dialogs.you_win_fight
                player.states.main_state = 1
                enemy.states.main_state = 1
                keyboard = keyboards.street()
                enemy_keyboard = "street"
            else:
                keyboard = keyboards.fight_keyboard()
                enemy_keyboard = "fight_keyboard"
                text = dialogs.get_damage_message(False, hit_status, hit_name, damage, player, enemy)
                text += dialogs.choice_hit
                enemy_text = dialogs.get_damage_message(True, hit_status, hit_name, damage, enemy, player)
                enemy_text += dialogs.choice_guard

        player.clear_event_info()
        enemy.clear_event_info()

    else:
        player.event_stuff.info = player_choice
        text = dialogs.wait_the_enemy
        keyboard = keyboards.fight_keyboard(hide_buttons=True)

    await redis_queries.add_player(pool=pool, player=enemy)
    await redis_queries.add_player(pool=pool, player=player)

    await message.answer(text=text, keyboard=keyboard)
    if enemy_text:
        await stuff.send_message_to_right_platform(enemy, web_app, enemy_text, enemy_keyboard)


@vk_bot.message_handler(payload={"command": "stop_search_fight"}, state={"main_state": 20})
async def stop_search_fight(message: Message):
    player = message.player
    web_app = message.web_app
    player.states.main_state = 1
    player.states.upgrade_state = 0
    await web_app.add_player_to_redis(player)
    await redis_queries.add_await_fight(pool=web_app.redis_pool, fight=None)
    await message.answer(text=dialogs.scared, keyboard=keyboards.street())


@vk_bot.message_handler(payload={"command": "give_up"}, state={"main_state": 20})
async def give_up(message: Message):
    player = message.player
    web_app = message.web_app
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
    await message.answer(text=dialogs.you_give_up, keyboard=keyboards.street())


@vk_bot.message_handler(text="*", state={"main_state": 20})
async def fight_other(message: Message):
    await message.answer(text=dialogs.touch_buttons)


# =================================
@vk_bot.message_handler(payload={"command": "settings"}, state={"main_state": 1})
async def settings(message: Message):
    await message.answer(text=dialogs.settings, keyboard=keyboards.settings())


@vk_bot.message_handler(payload={"command": "link_account"})
async def link_account(message: Message):
    player = message.player
    await message.answer(
        text=dialogs.link_account % (player.token, "telegram", "telegram"),
        keyboard=keyboards.link_account()
    )


@vk_bot.message_handler(payload={"command": "link_tlg"})
async def link_account(message: Message):
    player = message.player
    web_app = message.web_app
    player.states.main_state = 2
    await redis_queries.add_player(pool=web_app.redis_pool, player=player)
    await message.answer(text=dialogs.send_link_token, keyboard=keyboards.link_account())


@vk_bot.message_handler(state={"main_state": 2})
async def process_link(message: Message):
    pass


@vk_bot.message_handler(payload={"command": "cancel_link"})
async def link_account(message: Message):
    player = message.player
    web_app = message.web_app
    player.states.main_state = 1
    await redis_queries.add_player(pool=web_app.redis_pool, player=player)
    await message.answer(text=dialogs.settings, keyboard=keyboards.settings())


@vk_bot.message_handler(text="меню", state={"main_state": 1})
async def fight_other(message: Message):
    await message.answer(text=dialogs.home, keyboard=keyboards.home())


@vk_bot.message_handler(text="отключиться")
async def disconnect(message: Message):
    player = message.player
    web_app = message.web_app
    if player.states.main_state != 1:
        text = dialogs.finish_actions
        keyboard = None
    else:
        text = dialogs.disconnected
        await stuff.self_disconnect_player(web_app=web_app, player=player)
        keyboard = keyboards.connect()
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(text="*")
async def other(message: Message):
    await vk_bot.send_message(user_ids=message.from_id, text="Не знаю что ответить")
