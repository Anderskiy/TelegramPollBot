import asyncio
import json
import time

from tqdm import tqdm
from colorama import Fore, Style

from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher
from handler import basic

load_dotenv()

bot_token = os.getenv('TOKEN')
if not bot_token:
    print("Помилка при запуску бота: Не зайдено токену у файлі .env")
    exit()


bot = Bot(token=bot_token, parse_mode='MarkdownV2')
dp = Dispatcher()
dp.include_router(basic.rt)


async def main():
    bar = tqdm(total=100, desc="Вмикаємо бота...", bar_format=f"{Fore.GREEN}{{l_bar}}{{bar}}{{r_bar}}{Style.RESET_ALL}",
               ncols=100, ascii=True)
    try:
        bar.update(10)
        bar.refresh()
        time.sleep(0.5)
        with open('form.json', 'r', encoding='utf-8') as f:
            temp_data = json.load(f)

    except FileNotFoundError:
        return print("Помилка при запуску бота. Не знайдено файл конфігу: form.json")
    except json.JSONDecodeError:
        return print("Помилка при запуску бота. Щось у файлі form.json вказано неправильно.")
    except ValueError as ve:
        return print(f"Помилка при запуску бота: {ve}")
    except Exception as e:
        return print(f"При відкритті конфігу була виявлена помилка: {e}")
    finally:
        bar.update(10)
        bar.refresh()
        time.sleep(0.5)

    if not all(key in temp_data for key in ['слайди', 'фото', 'питання']):
        raise ValueError("Помилка при запуску бота. Відсутні дєякі ключі у файлі конфігу")

    bar.update(10)
    bar.refresh()

    if len(temp_data['слайди']) != len(set(temp_data['слайди'])):
        return print("Помилка при запуску бота. Є дублікати слайдів.")

    bar.update(10)
    bar.refresh()
    time.sleep(0.5)

    if temp_data['слайди'].keys() != temp_data['фото'].keys():
        return print("Помилка при запуску бота. Не рівна кількість питань і фото")

    bar.update(20)
    bar.refresh()

    tmp = 0
    for i in temp_data['слайди']:
        tmp += 1
        if i != f"{tmp}":
            return print("Помилка при запуску бота. Неправильно вказано порядок слайдів або їх назву(число у подвійних дужках)")
    bar.update(10)
    bar.refresh()
    tmp = 0
    for i in temp_data['фото']:
        tmp += 1
        if i != f"{tmp}":
            return print("Помилка при запуску бота. Неправильно вказано порядок слайдів або їх назву(число у подвійних дужках)")
    bar.update(10)
    bar.refresh()
    tmp = 0
    for i in temp_data['питання']:
        tmp += 1
        if i != f"{tmp}":
            return print("Помилка при запуску бота. Неправильно вказано порядок запитань або їх назву(число у подвійних дужках)")
        else:
            _tmp = 0
            for j in temp_data['питання'][i]['варіанти']:
                _tmp += 1
                if j != f"{_tmp}":
                    return print("Помилка при запуску бота. Неправильно вказано порядок відповідей або їх назву(число у подвійних дужках)")
            if str(temp_data['питання'][i]['правильний']) not in temp_data['питання'][i]['варіанти']:
                return print("Помилка при запуску бота. Неправильно вказана правильна відповідь")
    bar.update(10)
    bar.refresh()
    time.sleep(0.5)
    await bot.delete_webhook(drop_pending_updates=True)
    bar.update(10)
    bar.refresh()
    time.sleep(0.5)
    bar.close()
    bot_me = await bot.me()
    print(f"Бот {bot_me.first_name} успішно ввімкнений!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())