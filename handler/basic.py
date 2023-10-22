from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.exceptions import TelegramBadRequest

from contextlib import suppress

import keyboards.inline
from keyboards.reply import main_kb
from keyboards.inline import paginator

rt = Router()

data = [
    ["first"],
    ["second"],
    ["third"],
    ["four"]
]

@rt.message(CommandStart())
async def start(message: Message):
    print(message)
    await message.answer(f"💖 Спасибо что воспользовались нашим ботом, {message.from_user.first_name}",
                         reply_markup=main_kb)

@rt.callback_query(keyboards.inline.Pagination.filter(F.action.in_(["prev", "next"])))
async def pafination_handler(call: CallbackQuery, callback_data: keyboards.inline.Pagination):
    page_num = int(callback_data.page)
    page = page_num - 1 if page_num >= 0 else 0

    with suppress(TelegramBadRequest):
        if callback_data.action == "next":
            page = page_num + 1 if page_num < (len(data) - 1) else page_num

        await call.message.edit_text(f"{data[page]}", reply_markup=keyboards.inline.paginator(page))
    await call.answer()

@rt.callback_query(keyboards.inline.Pagination.filter(F.action.in_("close")))
async def close_handler(call: CallbackQuery):
    await call.message.delete()
    await call.answer()

@rt.message()
async def echo(message: Message):
    msg = message.text.lower()

    if msg == "что я умею?":
        await message.answer("Пока что ничего, но очень скоро буду рассказывать про космос!")
    elif msg == "высадке на луну 50 лет!":
        await message.answer(f"{data[0]}", reply_markup=paginator())