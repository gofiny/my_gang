from config import TLG_API_KEY
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from common_utils import dialogs
from vk_api.vk import Message as VkMessage


tlg_bot = Bot(TLG_API_KEY)
dp = Dispatcher(tlg_bot)


async def register_request(message: VkMessage):
    await tlg_bot.send_message(chat_id=message.from_id, text=dialogs.reg_start)


@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.answer(text="Hello! That`s good!")


@dp.message_handler()
async def other_messages(message: Message):
    await message.answer(text="It`s work!")
