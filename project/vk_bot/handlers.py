from vk_api.vk import Message, VK
from config import VK_API_KEY, VK_API_VER
from vk_bot import keyboards
from common_utils import dialogs, exceptions
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
    keyboard = keyboards.street(level=message.player.level)
    await message.answer(text=dialogs.street, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "choose_upgrade"})
async def choose_upgrade(message: Message):
    await message.answer(text=dialogs.choose_upgrade, keyboard=keyboards.choose_upgrade())


@vk_bot.message_handler(payload={"command": "choose_power"})
async def choose_power(message: Message):
    await message.answer(text=dialogs.power_active_start, keyboard=keyboards.power_active_start())


@vk_bot.message_handler(payload={"command": "power_active_start"})
async def power_active_start(message: Message):
    web_app = message.web_app
    player = message.player
    player.states.main_state = 10
    player.states.power_stage = 0
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.power_active_down, keyboard=keyboards.power_active())


@vk_bot.message_handler(payload={"command": "power_action_up"}, state={"main_state": 10})
async def power_action(message: Message):
    player = message.player
    if player.states.power_state % 2 != 0:
        player.states.power_state += 1
        text = dialogs.power_active_down
        keyboard = keyboards.power_active()
    else:
        player.states.main_state = 1
        player.states.power_state = 0
        text = dialogs.power_active_stop
        keyboard = keyboards.choose_upgrade()

    await message.web_app.add_player_to_redis(player)
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "power_action_down"}, state={"main_state": 10})
async def power_action(message: Message):
    player = message.player
    if player.states.power_state % 2 == 0:
        player.states.power_state += 1
        text = dialogs.power_active_up
        keyboard = keyboards.power_active()
    else:
        player.states.main_state = 1
        player.states.power_state = 0
        text = dialogs.power_active_stop
        keyboard = keyboards.choose_upgrade()

    await message.web_app.add_player_to_redis(player)
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(payload={"command": "power_action_stuff"}, state={"main_state": 10})
async def power_action(message: Message):
    player = message.player
    player.states.main_state = 1
    player.states.power_state = 0

    await message.web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.power_active_stuff, keyboard=keyboards.choose_upgrade())


@vk_bot.message_handler(payload={"command": "power_active_stop"})
async def power_active_stop(message: Message):
    message.player.states.main_state = 1
    message.player.states.power_state = 0
    await message.web_app.add_player_to_redis(message.player)
    await message.answer(text=dialogs.power_active_stop, keyboard=keyboards.choose_upgrade())


@vk_bot.message_handler(text="*")
async def other(message: Message):
    await vk_bot.send_message(user_ids=message.from_id, text="Не знаю что ответить")
