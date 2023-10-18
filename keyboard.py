from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Что я умею?")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбирете действия",
        selective=True
    )