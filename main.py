import asyncio
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher

from handler import basic

load_dotenv()
bot = Bot(token=(os.getenv('TOKEN')), parse_mode='MarkdownV2')
dp = Dispatcher()
dp.include_router(basic.rt)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())