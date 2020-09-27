from aiohttp.web import Application, Response, Request, post, run_app
from typing import Optional


class WebApp:
    def __init__(self, address_prefix: str,  secret_str: str, returning_callback_str: str):
        self.secret_str = secret_str
        self.app = Application()
        self.returning_callback_str = returning_callback_str
        self._set_base_handler(address_prefix=address_prefix)

    def _set_base_handler(self, address_prefix: str):
        self.app.add_routes([post(f"{address_prefix}/", self._base_handler)])

    async def _base_handler(self, request: Request) -> Response:
        request_json = await request.json()
        if request_json.get("secret") != self.secret_str:
            return Response(status=404)
        if request_json.get("type") == "confirmation":
            return Response(body=self.returning_callback_str)

        return Response(body="ok")

    def start_app(self, socket_path=None):
        run_app(self.app, path=socket_path)
