import asyncio
import json
import time

from tqdm import tqdm
from colorama import Fore, Style

from config import TOKEN

from aiogram import Bot, Dispatcher
from handler import basic, admin


if TOKEN == '':
    print("Помилка | Помилка при запуску бота: Не зайдено токену у файлі config.py")
    exit()


bot = Bot(token=TOKEN, parse_mode='HTML')
dp = Dispatcher()
dp.include_routers(
    admin.rt,
    basic.rt
)


async def main():
    def update_bar(increment: int, t: float = 0):
        bar.update(increment)
        bar.refresh()
        time.sleep(t)
    bar = tqdm(total=100, desc="Вмикаю бота...", bar_format=f"{Fore.GREEN}{{l_bar}}{{bar}}{{r_bar}}{Style.RESET_ALL}",
               ncols=100, ascii=True)
    try:
        update_bar(10, t=0.2)
        with open('form.json', 'r', encoding='utf-8') as f:
            temp_data = json.load(f)

    except FileNotFoundError as e:
        return print(f"Помилка | Помилка при запуску бота: {e.strerror}: {e.filename}")
    except (json.JSONDecodeError, ValueError) as e:
        return print(f"Помилка | Помилка при запуску бота: {str(e)}")
    except Exception as e:
        return print(f"Помилка | При відкритті конфігу була виявлена помилка: {e}")
    finally:
        update_bar(10, t=0.2)

    required_keys = ['слайди', 'фото', 'питання']
    if not all(key in temp_data for key in required_keys):
        raise ValueError("Помилка | Помилка при запуску бота. Відсутні деякі ключі у файлі конфігу")

    update_bar(10)

    if len(temp_data['слайди']) != len(set(temp_data['слайди'])):
        return print("Помилка | Помилка при запуску бота. Є дублікати слайдів.")

    update_bar(10, t=0.2)
    update_bar(20)

    for key in ['слайди', 'фото', 'питання']:
        for idx, item in enumerate(temp_data[key], start=1):
            if item != str(idx):
                return print(f"Помилка | Помилка при запуску бота. Неправильно вказано порядок {key} або їх назву(число у подвійних дужках)")
            if key == 'питання':
                for jdx, option in enumerate(temp_data[key][item]['варіанти'], start=1):
                    if option != str(jdx):
                        return print("Помилка при запуску бота. Неправильно вказано порядок відповідей або їх назву(число у подвійних дужках)")
                if str(temp_data['питання'][item]['правильний']) not in temp_data['питання'][item]['варіанти']:
                    return print("Помилка | Помилка при запуску бота. Неправильно вказана правильна відповідь")

    update_bar(10, t=0.2)
    await bot.delete_webhook(drop_pending_updates=True)
    update_bar(10, t=0.2)
    update_bar(20, t=0.2)
    bar.close()
    bot_me = await bot.me()
    print(f"Бот | {bot_me.first_name} успішно ввімкнений!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())