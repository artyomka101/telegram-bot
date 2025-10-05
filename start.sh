#!/bin/bash
# Скрипт запуска для Timeweb

echo "Starting Telegram Bot on Timeweb..."

# Проверяем токен
if [ -z "$BOT_TOKEN" ]; then
    echo "Error: BOT_TOKEN environment variable is not set!"
    exit 1
fi

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting bot..."
python bot.py
