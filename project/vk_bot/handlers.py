from vk_api.vk import Message, VK
from config import VK_API_KEY, VK_API_VER
from vk_bot import keyboards
from common_utils import dialogs

vk_bot = VK(VK_API_KEY, VK_API_VER)


@vk_bot.message_handler(payload={"command": "start"})
async def start_message(message: Message):
    user = message.user
    await message.answer(text=f"user: {user.user_id} if_foled: {user.is_followed}", keyboard=keyboards.info_payload())


@vk_bot.message_handler(payload={"command": "disconnected"})
async def connect_request(message: Message):
    pass


@vk_bot.message_handler(payload={"command": "register"})
async def register_request(message: Message):
    await message.answer(text=dialogs.reg_start, keyboard=keyboards.empty_keyboard())


@vk_bot.message_handler(text="*")
async def other(message: Message):
    await vk_bot.send_message(user_ids=message.from_id, text="Не знаю что ответить")
