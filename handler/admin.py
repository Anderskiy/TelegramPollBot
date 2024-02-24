from aiogram.filters import Command
from aiogram.filters.command import CommandObject

from filters.isadmin import IsAdmin

from utils.general import *

rt = Router()

@rt.message(IsAdmin(), Command("answers", "відповіді", prefix="!"))
async def answer(message: Message):
    answers = await AioMember.get_all_results()
    if not answers:
        return await message.answer("Наразі немає ні одної відповіді")
    answer_text = "\n".join(f"* {member}: {result}" for member, result in answers)
    await message.answer(f"<b>Результати опитування:</b>\n{answer_text}")

@rt.message(IsAdmin(), Command("clear", "очистити", prefix="!"))
async def clear_table(message: Message, command: CommandObject):
    if not command.args:
        return await message.answer("Помилка! Неправильно передано аргументи команди.\n > !clear/очистити @username")

    for arg in command.args.split(chr(32)):
        if arg.startswith('@'):
            res = await AioMember.clear_one(arg)
            if not res:
                return await message.answer("Цей користувач ще не проходив вікторину")
            return await message.answer("Таблицю було успішно очищено.")
        if arg == "all" or arg == "все":
            await AioMember.truncate()
            return await message.answer("Таблицю було успішно очищено.")
    return await message.answer("Введіть згадку про користувача в правильному вигляді:\n > !clear/очистити @username")
