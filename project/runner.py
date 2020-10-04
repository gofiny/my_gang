import argparse
import asyncio
from vk_bot.handlers import vk_bot
from tlg_bot.handlers import dp
from applications.web_app import WebApp
from config import (
    VK_ADDRESS_PREFIX,
    TLG_ADDRESS_PREFIX,
    SECRET_STR,
    RETURING_CALLBACK_STR,
    PG_DESTINATION,
    REDIS_ADDRESS
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path")
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    app = WebApp(
        tlg_address_prefix=TLG_ADDRESS_PREFIX,
        vk_address_prefix=VK_ADDRESS_PREFIX,
        secret_str=SECRET_STR,
        returning_callback_str=RETURING_CALLBACK_STR,
        vk_bot=vk_bot,
        tlg_dp=dp
    )
    loop.run_until_complete(app.prepare(PG_DESTINATION, REDIS_ADDRESS))
    app.start_app(socket_path=args.path)
