import argparse
from web_app import WebApp
from config import DEBUG_SECRET_STR, DEBUG_RETURING_CALLBACK_STR


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path")
    args = parser.parse_args()
    app = WebApp(
        address_prefix="my_gang_debug",
        secret_str=DEBUG_SECRET_STR,
        returning_callback_str=DEBUG_RETURING_CALLBACK_STR
    )

    app.start_app(socket_path=args)
