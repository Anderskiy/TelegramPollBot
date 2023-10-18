from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.reply import main_kb

rt = Router()

@rt.message(CommandStart())
async def start(message: Message):
    print(message)
    await message.answer(f"💖 Спасибо что воспользовались нашим ботом, {message.from_user.first_name}",
                         reply_markup=main_kb)

@rt.message()
async def echo(message: Message):
    msg = message.text.lower()

    if msg == "что я умею?":
        await message.answer("Пока что ничего, но очень скоро буду рассказывать про космос!")