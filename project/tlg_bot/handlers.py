from config import TLG_API_KEY
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message
from tlg_bot import keyboards
from db_utils import pg_queries
from common_utils import dialogs, exceptions, stuff


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
        player = await web_app.get_player_from_pg(connection=connection, player_uuid=player_uuid)
        player.states.main_state = 1
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.main_menu, reply_markup=keyboards.main_menu())


@dp.message_handler(commands=["start"])
async def start(message: Message):
    web_app = message.conf["web_app"]
    player = message.conf["player"]
    player.states.main_state = 1
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.main_menu, reply_markup=keyboards.main_menu())


@dp.message_handler(pl_state={"main_state": 0})
async def register_name(message: Message):
    web_app = message.conf["web_app"]
    player = message.conf["player"]
    keyboard = None
    try:
        if len(message.text) > 30 or len(message.text) < 4:
            raise exceptions.NotCorrectName
        #if stuff.name_validation(message.text):
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
    text = dialogs.my_profile % (player.name, player.level, player.respect, 0, player.power, player.health, player.mind)
    await message.answer(text=text)


@dp.message_handler()
async def other_messages(message: Message):
    await message.answer(text="It`s work!")
