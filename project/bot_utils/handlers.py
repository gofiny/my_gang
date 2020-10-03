from db_utils.models import User
from vk_api.vk import Message, VK, Keyboard
from config import API_KEY, API_VER
from bot_utils import keyboards, dialogs
from db_utils import pg_queries

bot = VK(API_KEY, API_VER)


def get_sub_keyboard(user: User) -> Keyboard:
    if user.is_followed:
        keyboard = keyboards.unsubscribe()
    else:
        keyboard = keyboards.subscribe()

    return keyboard


@bot.message_handler(payload={"command": "start"})
async def start_message(message: Message):
    keyboard = get_sub_keyboard(message.user)
    await message.answer(text=dialogs.start, keyboard=keyboard)
    await message.answer(text=dialogs.telegram_request, keyboard=keyboards.telegram_link())


@bot.message_handler(payload={"command": "subscribe"})
async def subscribe(message: Message):
    user = message.user
    user.is_followed = True
    await pg_queries.change_subscribe(pool=message.app.get_pg_pool(), user=user)
    await message.answer(text=dialogs.subscribe, keyboard=keyboards.unsubscribe())


@bot.message_handler(payload={"command": "unsubscribe"})
async def unsubscribe(message: Message):
    user = message.user
    user.is_followed = False
    await pg_queries.change_subscribe(pool=message.app.get_pg_pool(), user=user)
    await message.answer(text=dialogs.unsubscribe, keyboard=keyboards.subscribe())


@bot.message_handler(text="*")
async def other(message: Message):
    keyboard = get_sub_keyboard(user=message.user)
    await message.answer(text=dialogs.other_message, keyboard=keyboard)
    await message.answer(text=dialogs.telegram_request, keyboard=keyboards.telegram_link())
