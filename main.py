import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import router

# Render beradigan PORT ni o'qib olamiz (standart 10000 bo'ladi)
PORT = int(os.environ.get("PORT", 10000))

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"HTTP Server {PORT}-portda ishga tushdi.")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    # Port timeout bermasligi uchun soxta Web Serverni parallel yurgizamiz
    await start_dummy_server()
    
    logging.info("Bot polling boshlandi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())