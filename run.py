import subprocess
import sys
import os

print("Бот | Встановлюю залежності...")

if not os.path.exists('requirements.txt'):
    print(f"Помилка | Файл requirements.txt не знайдено.")
    sys.exit(1)

try:
    with open(os.devnull, 'w') as null:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], stdout=null, stderr=null)
except subprocess.CalledProcessError as e:
    print(f"Помилка | Сталася помилка під час встановлення залежностей: {e}")
    sys.exit(1)

if os.name == 'nt':  # для Windows
    subprocess.call('cls', shell=True)
else:  # для macOS и Linux
    subprocess.call('clear', shell=True)

if not os.path.exists('config.py'):
    print(f"Помилка | Файл config.py не знайдено.")
    sys.exit(1)

try:
    subprocess.run([sys.executable, 'bot.py'])
except FileNotFoundError:
    print(f"Помилка | Файл bot.py не знайдено.")
    sys.exit(1)