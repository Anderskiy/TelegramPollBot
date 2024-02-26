from aiogram.types import Message
from aiogram.filters import BaseFilter
from config import ADMIN_USERNAME

class IsAdmin(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, message: Message):
        user_username = message.from_user.username
        if user_username is None:
            return False
        return user_username == ADMIN_USERNAME or "@" + user_username == ADMIN_USERNAME