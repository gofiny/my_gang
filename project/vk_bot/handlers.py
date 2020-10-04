from vk_api.vk import Message, VK
from config import VK_API_KEY, VK_API_VER
from vk_bot import keyboards

vk_bot = VK(VK_API_KEY, VK_API_VER)


@vk_bot.message_handler(payload={"command": "start"})
async def start_message(message: Message):
    user = message.user
    await message.answer(text=f"user: {user.user_id} if_foled: {user.is_followed}", keyboard=keyboards.info_payload())


@vk_bot.message_handler(text="test")
async def text_test(message: Message):
    await vk_bot.send_message(user_ids=message.from_id, text="text work", keyboard=keyboards.payload_start())


@vk_bot.message_handler(text="send info")
async def test_payload_info(message: Message):
    info = message.payload["info"]
    await vk_bot.send_message(user_ids=message.from_id, text=f"payload info: {info}")


@vk_bot.message_handler(text="test keyboard")
async def test_keyboard(message: Message):
    keyboard = keyboards.test_count_buttons(41)
    await vk_bot.send_message(user_ids=message.from_id, text="see:", keyboard=keyboard)


@vk_bot.message_handler(text="*")
async def other(message: Message):
    await vk_bot.send_message(user_ids=message.from_id, text="Не знаю что ответить")
