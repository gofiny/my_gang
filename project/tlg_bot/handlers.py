from config import TLG_API_KEY
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message
from tlg_bot import keyboards
from common_utils import dialogs


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


@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.answer(text="Hello! That`s good!")


@dp.message_handler(pl_state={"main_state": 0})
async def test_states(message: Message):
    await message.answer(text="God damn it, work!")


@dp.message_handler()
async def other_messages(message: Message):
    await message.answer(text="It`s work!")
