from aiohttp import web


async def test(request):
    return web.Response(text="ok")


app = web.Application()
app.add_routes([web.get("/", test)])

web.run_app(app)
