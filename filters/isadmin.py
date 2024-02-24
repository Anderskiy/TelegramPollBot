from aiogram.types import Message
from aiogram.filters import BaseFilter
from config import ADMIN_USERNAME

class IsAdmin(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, message: Message):
        return message.from_user.username == ADMIN_USERNAME or "@" + message.from_user.username == ADMIN_USERNAME