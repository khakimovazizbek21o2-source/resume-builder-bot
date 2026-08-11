import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher

# 1. Botingiz va Routerni import qiling
from handlers import router  # <-- O'zingizning handlers faylingiz nomini kiriting

TOKEN = os.getenv("BOT_TOKEN", "8668763966:AAGOSeYgbeWGwsv-nRFtfONwpPCSMvIAwLM")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 2. ROUTER'NI DISPATCHER'GA ULASH (MUHIM!)
dp.include_router(router)

PORT = int(os.environ.get("PORT", 10000))

async def handle_ping(request):
    return web.Response(text="Bot is live!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

async def main():
    await start_dummy_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
