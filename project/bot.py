from config import API_VER, API_KEY, DEBUG_API_KEY
from vk import VK, Message, Keyboard, Button


bot = VK(DEBUG_API_KEY, API_VER)


@bot.message_handler(payload={"command": "start"})
async def start_message(message: Message):
    pass


@bot.message_handler("test")
async def test(message: Message):
    await bot.send_message(user_ids=message.from_id, text="its work")
