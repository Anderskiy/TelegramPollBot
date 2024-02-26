from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Що я вмію?")],
            [KeyboardButton(text="Переглянути презентацію")],
            [KeyboardButton(text="Пройти вікторину")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Виберіть дії",
        selective=True
    )