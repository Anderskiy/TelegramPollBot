@echo off

if not exist requirements.txt (
    echo Файл requirements.txt не знайдено.
    exit /b
)

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Сталася помилка під час встановлення залежностей.
    exit /b
)

cls

python main.py

pause