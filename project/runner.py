import argparse
from handlers import bot
from web_app import WebApp
from config import ADDRESS_PREFIX, SECRET_STR, RETURING_CALLBACK_STR


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path")
    args = parser.parse_args()
    app = WebApp(
        address_prefix=ADDRESS_PREFIX,
        secret_str=SECRET_STR,
        returning_callback_str=RETURING_CALLBACK_STR,
        bot=bot
    )
    app.start_app(socket_path=args.path)
