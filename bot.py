#!/usr/bin/env python3
"""
Простой Telegram бот для Timeweb
Все в одном файле для простого развертывания
"""

import os
import logging
import json
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# Файл для данных
DATA_FILE = "bot_data.json"

def load_data():
    """Загрузить данные из файла"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"subjects": [], "messages_count": 0}

def save_data(data):
    """Сохранить данные в файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🤖 Привет! Я простой бот для управления предметами.\n\n"
        "Доступные команды:\n"
        "/help - Показать справку\n"
        "/subjects - Показать предметы\n"
        "/add_subject - Добавить предмет\n"
        "/stats - Статистика"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📚 Доступные команды:

/start - Начать работу с ботом
/help - Показать эту справку
/subjects - Показать список предметов
/add_subject - Добавить новый предмет
/stats - Показать статистику

💡 Просто отправьте любое сообщение, и я отвечу!
"""
    await update.message.reply_text(help_text)

async def subjects_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /subjects"""
    data = load_data()
    subjects = data.get("subjects", [])
    
    if not subjects:
        await update.message.reply_text("📝 Список предметов пуст.\nИспользуйте /add_subject для добавления предметов.")
    else:
        subjects_text = "📚 Список предметов:\n\n" + "\n".join(f"• {subject}" for subject in subjects)
        await update.message.reply_text(subjects_text)

async def add_subject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /add_subject"""
    data = load_data()
    if "subjects" not in data:
        data["subjects"] = []
    
    # Добавляем тестовый предмет
    new_subject = f"Предмет {len(data['subjects']) + 1}"
    data["subjects"].append(new_subject)
    save_data(data)
    
    await update.message.reply_text(f"✅ Добавлен предмет: {new_subject}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    data = load_data()
    subjects_count = len(data.get("subjects", []))
    messages_count = data.get("messages_count", 0)
    
    await update.message.reply_text(
        f"📊 Статистика:\n\n"
        f"📚 Предметов: {subjects_count}\n"
        f"💬 Сообщений: {messages_count}\n"
        f"🏠 Хостинг: Timeweb"
    )

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_text = update.message.text
    
    # Увеличиваем счетчик сообщений
    data = load_data()
    data["messages_count"] = data.get("messages_count", 0) + 1
    save_data(data)
    
    await update.message.reply_text(f"💬 Вы написали: {user_text}\n\nИспользуйте /help для получения списка команд.")

def main():
    """Главная функция"""
    # Получаем токен бота
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logging.error("BOT_TOKEN environment variable is not set!")
        return
    
    logging.info("Starting Telegram bot...")
    
    # Создаем приложение
    application = Application.builder().token(bot_token).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("subjects", subjects_command))
    application.add_handler(CommandHandler("add_subject", add_subject_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo_message))
    
    # Запускаем бота
    logging.info("Bot is starting...")
    try:
        application.run_polling(close_loop=False, drop_pending_updates=True)
    except Exception as e:
        logging.error(f"Bot error: {e}")

if __name__ == "__main__":
    main()
