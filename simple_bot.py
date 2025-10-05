#!/usr/bin/env python3
"""
Simple Telegram Bot for Scalingo deployment
All code in one file to avoid import issues
"""

import os
import sys
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
import json


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# Simple data storage
DATA_FILE = "data.json"

def load_data():
    """Load data from JSON file"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"subjects": [], "schedule": {}}

def save_data(data):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Health check server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    """Start a simple HTTP server for health checks"""
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "Привет! Я бот для управления расписанием.\n"
        "Используйте /help для получения списка команд."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
Доступные команды:
/start - Начать работу с ботом
/help - Показать это сообщение
/subjects - Показать список предметов
/add_subject - Добавить предмет
"""
    await update.message.reply_text(help_text)

async def subjects_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subjects command"""
    data = load_data()
    subjects = data.get("subjects", [])
    
    if not subjects:
        await update.message.reply_text("Список предметов пуст.")
    else:
        subjects_text = "Список предметов:\n" + "\n".join(f"• {subject}" for subject in subjects)
        await update.message.reply_text(subjects_text)

async def add_subject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add_subject command"""
    # Simple implementation - just add a test subject
    data = load_data()
    if "subjects" not in data:
        data["subjects"] = []
    
    data["subjects"].append("Новый предмет")
    save_data(data)
    
    await update.message.reply_text("Предмет добавлен!")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    await update.message.reply_text(f"Вы написали: {update.message.text}")

def main():
    """Main function to start the bot"""
    # Start health check server in a separate thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Get bot token from environment
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logging.error("BOT_TOKEN environment variable is not set!")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("subjects", subjects_command))
    application.add_handler(CommandHandler("add_subject", add_subject_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo_message))
    
    # Start bot
    logging.info("Starting bot...")
    application.run_polling(close_loop=False, drop_pending_updates=True)

if __name__ == "__main__":
    main()
