import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher

# Render bergan PORT'ni olish
PORT = int(os.environ.get("PORT", 8080))

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

async def main():
    # Soxta web serverni orqa fonda ishga tushirish
    await start_dummy_server()
    
    # Botingizning odatiy polling qismi
    # await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())