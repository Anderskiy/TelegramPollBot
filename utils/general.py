import json
import asyncio
from aiogram.types import Message

user_scores = {}
question_ids = {}
poll_timers = {}
sent_polls = {}


with open('form.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

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