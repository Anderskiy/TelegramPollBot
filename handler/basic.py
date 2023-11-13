from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from contextlib import suppress

import keyboards.inline
from keyboards.reply import main_kb
from keyboards.inline import paginator

rt = Router()

data = [
    ["*Первая высадка на луну*\n"
     "Данное мировое событие произошло во время операции \"Апполон\-11\", которую возглавляли США и НАСА\.\n"
     "Полет стартовал 16 июля 1969 года из Флориды\. Ровно в 13:32:00 UTC\.",
     "https://cdn.discordapp.com/attachments/1060667113494302720/1165709515325452388/first.jpg?ex=65638616&is=65511116&hm=8b05bc379dc81df42ac7a8beef26668370f1ba08da3d1945724105366796fa9c&"],
    ["*Экипаж*\n"
     "Командир — Нил Армстронг \(2\-й космический полёт\)\.\n"
     "Пилот командного модуля — Майкл Коллинз \(2\-й космический полёт\)\.\n"
     "Пилот лунного модуля — Эдвин Олдрин \(2\-й космический полёт\)\.",
     "https://cdn.discordapp.com/attachments/1060667113494302720/1173704647920332901/9k.png?ex=6564eca2&is=655277a2&hm=45c84125393d9d648b769e5e837119264671ef58977da3b4f76f51c69c05507c&"],
    ["*Первый шаг на луну*\n"
     "Первым человеком, ступившим на Луну, стал Нил Армстронг\. Это произошло 21 июля, в 02:56:15 UTC\. Через 15 минут к нему присоединился Эдвин Олдрин\.\n"
     "Астронавты установили в месте посадки флаг США, разместили комплект научных приборов и собрали 21,55 кг образцов лунного грунта\.",
     "https://cdn.discordapp.com/attachments/1060667113494302720/1173705391083880548/E87CC2AE-69B6-4A43-B120-879CF27C55D3_cx0_cy11_cw0_w408_r1.png?ex=6564ed53&is=65527853&hm=ac7f6d61df1e1c084814d2913ecd0f8bee2f1a44207fb422efdf5b55046191a9&"],
    ["fourth",
     "https://cdn.discordapp.com/attachments/1060667113494302720/1165709515795206244/third.jpeg?ex=65638616&is=65511116&hm=0ac44dbcffa695f8333d2201eec4c888c81228fc902d40fc9422456533329952&"]
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

        await call.message.delete()
        await call.message.answer_photo(photo=data[page][1], caption=data[page][0], reply_markup=keyboards.inline.paginator(page))
    await call.answer()

@rt.callback_query(keyboards.inline.Pagination.filter(F.action.in_("close")))
async def close_handler(call: CallbackQuery):
    await call.message.delete()
    await call.answer()

@rt.message()
async def echo(message: Message):
    msg = message.text.lower()

    if msg == "что я умею?":
        await message.answer("Пока что ничего, но очень скоро буду рассказывать про космос\!")
    elif msg == "высадке на луну 50 лет!":
        await message.answer_photo(photo=data[0][1], caption=data[0][0], reply_markup=paginator())
        # await message.answer(f"{data[0]}", reply_markup=paginator())