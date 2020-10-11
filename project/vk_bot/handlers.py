from vk_api.vk import Message, VK
from config import VK_API_KEY, VK_API_VER
from vk_bot import keyboards
from common_utils import dialogs, exceptions
from db_utils import pg_queries

vk_bot = VK(VK_API_KEY, VK_API_VER)


@vk_bot.message_handler(payload={"command": "start"})
async def start_message(message: Message):

    await message.answer(text="Work", keyboard=keyboards.info_payload())


async def connect_request(message: Message):
    await message.answer(text=dialogs.req_connect, keyboard=keyboards.connect())


async def register_request(message: Message):
    await message.answer(text=dialogs.reg_start, keyboard=keyboards.empty_keyboard())


@vk_bot.message_handler(text="*", state={"main_state": 0})
async def register_name(message: Message):
    web_app = message.web_app
    player = message.player
    keyboard = None
    try:
        if len(message.text) > 30:
            raise exceptions.NameTooLong
        await pg_queries.open_connection(
            pool=web_app.pg_pool, func=pg_queries.set_name_to_player,
            name=message.text, player_uuid=player.uuid)
        text = dialogs.welcome % message.text
        keyboard = keyboards.main_menu()
        player.states.main_state = 1
        player.name = message.text
        await web_app.add_player_to_redis(player)
    except exceptions.NameAlreadyExists:
        text = dialogs.this_name_taken
    except exceptions.NameTooLong:
        text = dialogs.name_too_long
    await message.answer(text=text, keyboard=keyboard)


@vk_bot.message_handler(text="*")
async def other(message: Message):
    await vk_bot.send_message(user_ids=message.from_id, text="Не знаю что ответить")
