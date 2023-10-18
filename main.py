import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboard import main_kb

bot = Bot("6158954004:AAHK5Fe_3iiDDMZD_-Bv5sHNjiA00-1Zzjs")
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    print(message)
    await message.answer(f"💖 Спасибо что воспользовались нашим ботом, {message.from_user.first_name}",
                         reply_markup=main_kb)

@dp.message()
async def echo(message: Message):
    msg = message.text.lower()

    if msg == "что я умею?":
        await message.answer("Пока что ничего, но очень скоро буду рассказывать про космос!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())