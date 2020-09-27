from config import API_VER, API_KEY, DEBUG_API_KEY
from vk import VK, Message
import keyboards


bot = VK(DEBUG_API_KEY, API_VER)


@bot.message_handler(payload={"command": "start"})
async def start_message(message: Message):
    await bot.send_message(user_ids=message.from_id, text="payload work", keyboard=keyboards.info_payload())


@bot.message_handler(text="test")
async def text_test(message: Message):
    await bot.send_message(user_ids=message.from_id, text="text work", keyboard=keyboards.payload_start())


@bot.message_handler(text="send info")
async def test_payload_info(message: Message):
    info = message.payload["info"]
    await bot.send_message(user_ids=message.from_id, text=f"payload info: {info}")
