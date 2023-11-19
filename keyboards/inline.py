from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

class Pagination(CallbackData, prefix="dis"):
    action: str
    page: int

def paginator(page: int = 0):
    from handler.basic import data
    builder = InlineKeyboardBuilder()
    if page > 0:
        builder.add(InlineKeyboardButton(text="<-", callback_data=Pagination(action="prev", page=page).pack()))
    if page < len(data['слайды']) - 1:
        builder.add(InlineKeyboardButton(text="->", callback_data=Pagination(action="next", page=page).pack()))
    if page == len(data['слайды']) - 1:
        builder.add(InlineKeyboardButton(text="✕", callback_data=Pagination(action="close", page=page).pack()))
    return builder.as_markup()
