import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher

# 1. BOT VA DISPATCHER'NI SHU YERDA SHUNDAY E'LON QILING (YOKI IMPORT QILING)
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Router va handlerlarni ulaymiz (agar bo'lsa)
# dp.include_router(...)

PORT = int(os.environ.get("PORT", 10000))

async def handle_ping(request):
    return web.Response(text="Bot is live!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Dummy HTTP server started on port {PORT}")

async def main():
    await start_dummy_server()
    # Endi dp topiladi!
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
