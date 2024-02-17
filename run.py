import subprocess
import sys
import os

print("Встановлюю залежності...")

if not os.path.exists('requirements.txt'):
    print(f"Файл requirements.txt не знайдено.")
    sys.exit(1)

try:
    with open(os.devnull, 'w') as null:  # Перенаправляем вывод в никуда
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], stdout=null, stderr=null)
except subprocess.CalledProcessError as e:
    print(f"Сталася помилка під час встановлення залежностей: {e}")
    sys.exit(1)

if os.name == 'nt':  # для Windows
    subprocess.call('cls', shell=True)
else:  # для macOS и Linux
    subprocess.call('clear', shell=True)

try:
    subprocess.run([sys.executable, 'main.py'])
except FileNotFoundError:
    print(f"Файл main.py не знайдено.")
    sys.exit(1)