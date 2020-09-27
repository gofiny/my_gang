from vk_api.vk import Message, VK
from config import API_KEY, API_VER
from bot_utils import keyboards

bot = VK(API_KEY, API_VER)


@bot.message_handler(payload={"command": "start"})
async def start_message(message: Message):
    await message.answer(text="payload work", keyboard=keyboards.info_payload())


@bot.message_handler(text="test")
async def text_test(message: Message):
    await bot.send_message(user_ids=message.from_id, text="text work", keyboard=keyboards.payload_start())


@bot.message_handler(text="send info")
async def test_payload_info(message: Message):
    info = message.payload["info"]
    await bot.send_message(user_ids=message.from_id, text=f"payload info: {info}")


@bot.message_handler(text="test keyboard")
async def test_keyboard(message: Message):
    keyboard = keyboards.test_count_buttons(41)
    await bot.send_message(user_ids=message.from_id, text="see:", keyboard=keyboard)


@bot.message_handler(text="*")
async def other(message: Message):
    await bot.send_message(user_ids=message.from_id, text="Не знаю что ответить")
