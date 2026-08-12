import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher

# Botingizning mavjud importlari va sozlamalari (bot, dp, routerlar)
# ...

# Render taqdim etadigan PORT'ni olish (bo'lmasa 8080)
PORT = int(os.environ.get("PORT", 8080))

# Render portni skaner qilganda javob qaytaruvchi funksiya
async def handle_ping(request):
    return web.Response(text="Bot is live and running!")

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
    # 1. Port muammosini hal qilish uchun web serverni ishga tushiramiz
    await start_dummy_server()
    
    # 2. Telegram bot pollingini boshlaymiz
    # await dp.start_polling(bot)  <-- Botingizning mavjud polling kodi

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())