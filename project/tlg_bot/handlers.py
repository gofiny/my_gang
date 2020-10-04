from config import TLG_API_KEY
from aiogram import Bot, Dispatcher
from aiogram.types import Message


tlg_bot = Bot(TLG_API_KEY)
dp = Dispatcher(tlg_bot)


@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.answer(text="Hello! That`s good!")


@dp.message_handler()
async def other_messages(message: Message):
    await message.answer(text="It`s work!")
