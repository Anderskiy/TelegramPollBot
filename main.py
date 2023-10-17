import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

bot = Bot("6158954004:AAHK5Fe_3iiDDMZD_-Bv5sHNjiA00-1Zzjs")
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    print(message)
    await message.answer(f"💖 Спасибо что воспользовались нашим ботом, {message.from_user.first_name}")

@dp.message(Command("about"))
async def about(message: Message):
    await message.answer("Что умеет этот бот?")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())