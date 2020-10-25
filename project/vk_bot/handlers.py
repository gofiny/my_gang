from vk_api.vk import Message, VK
from config import VK_API_KEY, VK_API_VER
from vk_bot import keyboards
from common_utils import dialogs, exceptions, stuff
from db_utils import pg_queries


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
    text = dialogs.my_profile % (player.name, player.level.level, player.respect,
                                 player.level.level_max, player.power, player.health, player.mind)
    await message.answer(text=text)


@vk_bot.message_handler(payload={"command": "wallet"})
async def wallet(message: Message):
    player = message.player
    text = dialogs.wallet % player.wallet.dollars

    await message.answer(text=text)


@vk_bot.message_handler(payload={"command": "storage"})
async def storage(message: Message):
    player = message.player
    text = dialogs.storage(player)
    await message.answer(text=text)


@vk_bot.message_handler(payload={"command": "home"})
async def home(message: Message):
    await message.answer(text=dialogs.home, keyboard=keyboards.home())


@vk_bot.message_handler(payload={"command": "street"})
async def street(message: Message):
    keyboard = keyboards.street()
    await message.answer(text=dialogs.street, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "choose_upgrade"})
async def choose_upgrade(message: Message):
    await message.answer(text=dialogs.choose_upgrade, keyboard=keyboards.choose_upgrade())


# ===================== Power active upgrade =====================
@vk_bot.message_handler(payload={"command": "choose_power"})
async def choose_power(message: Message):
    await message.answer(text=dialogs.power_active_start, keyboard=keyboards.power_active_start())


@vk_bot.message_handler(payload={"command": "power_active_start"})
async def power_active_start(message: Message):
    web_app = message.web_app
    player = message.player
    player.states.main_state = 10
    player.states.upgrade_state = 0
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.power_active_down % 0, keyboard=keyboards.power_active())


@vk_bot.message_handler(payload={"command": "power_action_up"}, state={"main_state": 10})
async def power_action(message: Message):
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
        text = dialogs.power_active_stuff
        keyboard = keyboards.choose_upgrade()

    await message.web_app.add_player_to_redis(player)
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "power_action_down"}, state={"main_state": 10})
async def power_action(message: Message):
    player = message.player
    if player.states.upgrade_state % 2 == 0 and player.states.upgrade_state < 20:
        player.states.upgrade_state += 1
        text = dialogs.power_active_up
        keyboard = keyboards.power_active()
    elif player.states.upgrade_state == 20:
        player.health = player.health - 5 if player.health > 20 else player.health
        player.states.main_state = 1
        player.states.upgrade_state = 0
        text = dialogs.power_active_too_much
        keyboard = keyboards.choose_upgrade()
    else:
        player.states.main_state = 1
        player.states.upgrade_state = 0
        text = dialogs.power_active_stuff
        keyboard = keyboards.choose_upgrade()

    await message.web_app.add_player_to_redis(player)
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "power_action_stuff"}, state={"main_state": 10})
async def power_action(message: Message):
    player = message.player
    player.power = player.power - 5 if player.power > 5 else player.power
    player.states.main_state = 1
    player.states.upgrade_state = 0

    await message.web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.power_active_stuff, keyboard=keyboards.choose_upgrade())


@vk_bot.message_handler(payload={"command": "power_active_stop"}, state={"main_state": 10})
async def power_active_stop(message: Message):
    player = message.player
    if player.states.upgrade_state < 10:  # if lower than 5 reps
        power = 0
    elif player.states.upgrade_state <= 14:  # if lower than 7 reps
        power = 5
    else:
        power = player.states.upgrade_state // 2
    player.states.main_state = 1
    player.states.upgrade_state = 0
    player.power += power
    await message.web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.power_active_stop % power, keyboard=keyboards.choose_upgrade())


@vk_bot.message_handler(text="*", state={"main_state": 10})
async def power_active_stop(message: Message):
    await message.answer(text=dialogs.touch_buttons)


# ================= health active upgrade ================
@vk_bot.message_handler(payload={"command": "choose_health"})
async def choose_power(message: Message):
    await message.answer(text=dialogs.health_active_start, keyboard=keyboards.health_active_start())


@vk_bot.message_handler(payload={"command": "health_active_start"})
async def power_active_start(message: Message):
    web_app = message.web_app
    player = message.player
    way, picture = stuff.gen_random_way()
    player.add_event(event_info=way)
    player.states.main_state = 11
    player.states.upgrade_state = 0
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.health_active_choose_way % (picture, 0), keyboard=keyboards.health_active())


@vk_bot.message_handler(payload={"command": "health_turn"})
async def power_active_start(message: Message):
    web_app = message.web_app
    player = message.player
    keyboard = keyboards.choose_upgrade()
    if player.states.upgrade_state == 20:
        player.states.main_state = 1
        player.states.upgrade_state = 0
        player.health = player.health - 5 if player.health > 20 else player.health
        player.event_stuff = None
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
            player.event_stuff = None
    await web_app.add_player_to_redis(player)
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "health_active_stop"}, state={"main_state": 11})
async def power_active_start(message: Message):
    web_app = message.web_app
    player = message.player
    distance = player.states.upgrade_state

    if distance < 10:
        new_health = 0
    elif 10 < distance < 15:
        new_health = distance - 2
    else:
        new_health = distance

    player.health += new_health
    player.states.main_state = 1
    player.states.upgrade_state = 0
    player.event_stuff = None

    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.health_active_stop % new_health, keyboard=keyboards.choose_upgrade())


@vk_bot.message_handler(text="*", state={"main_state": 11})
async def health_active_stop(message: Message):
    await message.answer(text=dialogs.touch_buttons)


# ================= health active upgrade ================


@vk_bot.message_handler(text="*")
async def other(message: Message):
    await vk_bot.send_message(user_ids=message.from_id, text="Не знаю что ответить")
