import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import router

# Telegram bot tokeningizni o'zgaruvchiga qo'ying
BOT_TOKEN = "8668763966:AAGOSeYgbeWGwsv-nRFtfONwpPCSMvIAwLM"

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Router'ni ulash
    dp.include_router(router)
    
    # Webhook bo'lsa tozalab, pollingni boshlash
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
