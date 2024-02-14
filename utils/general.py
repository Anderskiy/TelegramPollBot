import json
import asyncio

from aiogram import Router
from aiogram.types import Message, User

from utils.abstract import AbstractSQLObject, AbstractCacheManager, abstract_sql

rt = Router()

user_scores = {}
question_ids = {}
poll_timers = {}
sent_polls = {}


try:
    with open('form.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print("Помилка при запуску бота. Щось у файлі form.json вказано неправильно.")
    exit()

class CommandError(Exception):
    def __init__(self, message=None, *args):
        if message is not None:
            super().__init__(message, *args)
        else:
            super().__init__(*args)


class CommandInvokeError(CommandError):
    def __init__(self, e):
        self.original = e
        super().__init__('Command raised an exception: {0.__class__.__name__}: {0}'.format(e))


class ProfileNotCreatedError(CommandInvokeError):
    pass

async def send_poll(message: Message, question_id: str, chat_id = None):
    if not chat_id:
        chat_id = message.chat.id
    question = data["питання"][question_id]
    options = [option for option in question["варіанти"].values()]
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
        return "балів"
    if user_score == 1:
        return "бал"
    elif user_score >= 25:
        return "балів"
    elif user_score >= 22:
        return "бала"
    elif user_score >= 5:
        return "балів"
    elif user_score >= 2:
        return "бала"

class AioMember(AbstractSQLObject):
    _table = 'users'
    _key_column = 'user_id'
    id: int
    username: str
    total = len(data['питання'])

    def __eq__(self, other):
        if isinstance(other, int):
            return other == self.id
        return other.id == self.id

    @property
    def incremental(self) -> list[str]:
        return ['currency', 'total_messages']

    @classmethod
    async def load(cls, user) -> 'AioMember':
        if isinstance(user, User):
            if user.is_bot:
                await user.bot.send_message(chat_id=user.id, text="Вибачте\, але таке з ботом не провернути")
            user_id = user.id
        else:
            user_id = user
        if user_id in profiles_cache:
            return profiles_cache[user_id]
        res = await cls.select(user_id=user_id)
        if not res:
            raise ProfileNotCreatedError(f'profile not created yet with id {user_id}')
        if user_id in profiles_cache:
            return profiles_cache[user_id]
        profiles_cache[user_id] = res
        return res

    @classmethod
    async def set_new_result(cls, res, user_id):
        await abstract_sql('UPDATE users SET result=%s WHERE user_id=%s', f"{res}/{cls.total}", user_id, fetch=True)


loop = asyncio.get_event_loop()


def update_cache():
    global profiles_cache
    profiles_cache = AbstractCacheManager(loop, 900)


profiles_cache = AbstractCacheManager(loop, 900)