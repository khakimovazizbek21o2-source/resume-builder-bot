import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from handlers import router

# Render taqdim etadigan PORT ni olish
PORT = int(os.environ.get("PORT", 10000))


# Render Health Check uchun oddiy HTTP web-server
async def handle(request):
  return web.Response(text="Bot is running!")


async def main():
  logging.basicConfig(level=logging.INFO)

  bot = Bot(token="8668763966:AAGOSeYgbeWGwsv-nRFtfONwpPCSMvIAwLM")
  dp = Dispatcher()
  dp.include_router(router)

  # 1. Aiohttp web serverini yaratish (Render Port bog'lanishi uchun)
  app = web.Application()
  app.router.add_get("/", handle)
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, "0.0.0.0", PORT)
  await site.start()
  print(f"HTTP Server started on port {PORT}")

  # 2. Telegram Bot pollingini ishga tushirish
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
