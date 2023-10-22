from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Что я умею?")],
            [KeyboardButton(text="Высадке на луну 50 лет!")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбирете действия",
        selective=True
    )