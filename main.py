import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher

# Botingiz ob'ektlari (bot, dp) shu yerda bo'lishi kerak
# ...

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
    # 1. Soxta web serverni orqa fonda yoqamiz
    await start_dummy_server()
    
    # 2. BOT POLLING (MUHIM: Bu qator async jarayonni to'xtatmay ushlab turadi)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
