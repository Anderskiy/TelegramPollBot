from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, PollAnswer
from aiogram.exceptions import TelegramBadRequest

from contextlib import suppress
import json
import asyncio

import keyboards.inline
from keyboards.reply import main_kb
from keyboards.inline import paginator

rt = Router()
user_scores = {}
question_ids = {}
poll_timers = {}
sent_polls = {}

with open('form.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

@rt.message(CommandStart())
async def start(message: Message):
    print(message)
    await message.answer(f"💖 Спасибо что воспользовались нашим ботом, {message.from_user.first_name}",
                         reply_markup=main_kb)

@rt.callback_query(keyboards.inline.Pagination.filter(F.action.in_(["prev", "next"])))
async def pagination_handler(call: CallbackQuery, callback_data: keyboards.inline.Pagination):
    page_num = int(callback_data.page)
    page = page_num - 1 if page_num >= 0 else 0

    with suppress(TelegramBadRequest):
        if callback_data.action == "next":
            page = page_num + 1 if page_num < (len(data['слайды']) - 1) else page_num

        await call.message.delete()
        await call.message.answer_photo(photo=data['фото'][str(page)], caption=data['слайды'][str(page)], reply_markup=keyboards.inline.paginator(page))
    await call.answer()

@rt.callback_query(keyboards.inline.Pagination.filter(F.action.in_("close")))
async def close_handler(call: CallbackQuery):
    await call.message.delete()
    await call.answer()

@rt.poll_answer()
async def poll_answer(quiz_answer: PollAnswer):
    question_id = question_ids[quiz_answer.poll_id]
    correct_option_id = int(data["вопросы"][question_id]["правильный"]) - 1

    if quiz_answer.user.id not in user_scores:
        user_scores[quiz_answer.user.id] = 0

    if quiz_answer.option_ids[0] == correct_option_id:
        user_scores[quiz_answer.user.id] = user_scores.get(quiz_answer.user.id, 0) + 1

    next_question_id = str(int(question_id) + 1)
    if next_question_id in data["вопросы"]:
        await send_poll(quiz_answer, next_question_id, chat_id=quiz_answer.user.id)
    else:
        await quiz_answer.bot.send_message(quiz_answer.user.id, f'Вы набрали {user_scores[quiz_answer.user.id]} {ball(user_scores[quiz_answer.user.id])}\.')
        user_scores.clear()

    poll_timers[quiz_answer.poll_id] = asyncio.create_task(delete_poll_after_timeout(quiz_answer.poll_id, 3, quiz=quiz_answer))

@rt.message()
async def echo(message: Message):
    msg = message.text.lower()
    print(message)

    if msg == "что я умею?":
        await message.answer("Пока что ничего, но очень скоро буду рассказывать про космос\!")
    elif msg == "высадке на луну 50 лет!":
        await message.answer_photo(photo=data['фото']['1'], caption=data['слайды']['1'], reply_markup=paginator())
    elif msg == "пройти викторину":
        await send_poll(message, "1")

async def send_poll(message: Message, question_id: str, chat_id = None):
    if not chat_id:
        chat_id = message.chat.id
    question = data["вопросы"][question_id]
    options = [option for option in question["варианты"].values()]
    sent_poll = await message.bot.send_poll(
        chat_id=chat_id,
        question=question["текст"],
        options=options,
        type='regular',
        is_anonymous=False,
        allows_multiple_answers=False
    )

    question_ids[sent_poll.poll.id] = question_id
    sent_polls[sent_poll.poll.id] = sent_poll

async def delete_poll_after_timeout(poll_id, timeout, quiz = None):
    try:
        await asyncio.sleep(timeout)
        sent_poll = sent_polls.get(poll_id)
        if sent_poll:
            await quiz.bot.delete_message(chat_id=quiz.user.id, message_id=sent_poll.message_id)
        del poll_timers[poll_id]
    except Exception as e:
        print(e)

def ball(user_score):
    if user_score < 1:
        return "баллов"
    if user_score == 1:
        return "балл"
    elif user_score >=2 and user_score <=4:
        return "балла"
    elif user_score >= 5:
        return "баллов"