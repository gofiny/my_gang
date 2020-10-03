import argparse
import asyncio
from bot_utils.handlers import bot
from applications.web_app import WebApp
from config import (
    ADDRESS_PREFIX,
    SECRET_STR,
    RETURING_CALLBACK_STR,
    PG_DESTINATION,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path")
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    app = WebApp(
        address_prefix=ADDRESS_PREFIX,
        secret_str=SECRET_STR,
        returning_callback_str=RETURING_CALLBACK_STR,
        bot=bot
    )
    loop.run_until_complete(app.prepare(PG_DESTINATION))
    app.start_app(socket_path=args.path)
