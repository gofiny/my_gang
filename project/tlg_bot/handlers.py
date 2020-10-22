from config import TLG_API_KEY
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message
from tlg_bot import keyboards
from db_utils import pg_queries
from common_utils import dialogs, exceptions


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


@dp.message_handler(text=["\U0001F4AA Сила"])
async def choose_power(message: Message):
    await message.answer(text=dialogs.power_active_start, reply_markup=keyboards.power_active_start())


@dp.message_handler(text=["\U0001F4AA Начать"])
async def power_active_start(message: Message):
    web_app = message.conf["web_app"]
    player = message.conf["player"]
    player.states.main_state = 10
    player.states.power_stage = 0
    await web_app.add_player_to_redis(player)
    await message.answer(text=dialogs.power_active_down, reply_markup=keyboards.power_active())


@dp.message_handler(text=["\U0000270B Поставить штангу"])
async def power_active_stop(message: Message):
    await message.answer(text=dialogs.power_active_stop, reply_markup=keyboards.choose_upgrade())


@dp.message_handler()
async def other_messages(message: Message):
    await message.answer(text="It`s work!")
