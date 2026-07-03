import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiohttp import web
from dotenv import load_dotenv

from app.database.models import async_main
from app.handlers import router

load_dotenv()

TOKEN = str(os.getenv("TOKEN"))

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def handle(request):
    return web.Response(text="Bot is alive!")


async def main():
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)

    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 8000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Сервер запущен на порту {port}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
