from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, PollAnswer

import keyboards.inline
from keyboards.reply import main_kb
from keyboards.inline import paginator

from utils.general import *

rt = Router()

@rt.message(CommandStart())
async def start(message: Message):
    print(message.from_user.usernameл, ": /start")
    await message.answer(f"💖 Дякую що скористалися нашим ботом, {message.from_user.first_name}",
                         reply_markup=main_kb)

@rt.callback_query(keyboards.inline.Pagination.filter(F.action.in_(["prev", "next"])))
async def pagination_handler(call: CallbackQuery, callback_data: keyboards.inline.Pagination):
    page_num = callback_data.page + 1 if callback_data.page == 0 else callback_data.page

    if callback_data.action == "next":
        page = page_num + 1
    if callback_data.action == "prev":
        page = page_num - 1

    await call.message.delete()
    try:
        await call.message.answer_photo(photo=data['фото'][str(page)], caption=data['слайди'][str(page)], reply_markup=keyboards.inline.paginator(page))
    except TelegramBadRequest as br:
        print(f"Сталася помилка при відправленні тексту або файлу: {br.message}")
    await call.answer()

@rt.callback_query(keyboards.inline.Pagination.filter(F.action.in_("close")))
async def close_handler(call: CallbackQuery):
    await call.message.delete()
    await call.answer()

@rt.poll_answer()
async def poll_answer(quiz_answer: PollAnswer):
    question_id = question_ids[quiz_answer.poll_id]
    correct_option_id = int(data["питання"][question_id]["правильний"]) - 1

    if quiz_answer.user.id not in user_scores:
        user_scores[quiz_answer.user.id] = 0

    if quiz_answer.option_ids[0] == correct_option_id:
        user_scores[quiz_answer.user.id] = user_scores.get(quiz_answer.user.id, 0) + 1

    next_question_id = str(int(question_id) + 1)
    if next_question_id in data["питання"]:
        await send_poll(quiz_answer, next_question_id, chat_id=quiz_answer.user.id)
    else:
        await quiz_answer.bot.send_message(quiz_answer.user.id, f'Ви набрали {user_scores[quiz_answer.user.id]} {ball(user_scores[quiz_answer.user.id])}.')
        await AioMember.set_new_result(user_scores[quiz_answer.user.id], quiz_answer.user.id)
        user_scores.clear()

    poll_timers[quiz_answer.poll_id] = asyncio.create_task(delete_poll_after_timeout(quiz_answer.poll_id, 3, quiz=quiz_answer))

@rt.message()
async def echo(message: Message):
    if message.from_user.is_bot:
        return
    try:
        await AioMember.load(message.from_user.id)
    except ProfileNotCreatedError:
        await AioMember.create_default(message.from_user.id, message.from_user.username)
    msg = message.text.lower()

    if msg == "що я вмію?":
        await message.answer("Поки що нічого цікавого\\.\\.\\.")
    elif msg == "висадці на місяць 50 років!":
        await message.answer_photo(photo=data['фото']['1'], caption=data['слайди']['1'], reply_markup=paginator())
    elif msg == "пройти вікторину":
        await send_poll(message, "1")
