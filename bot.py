#!/usr/bin/env python3
"""
Полнофункциональный Telegram бот для Timeweb
С интерактивными кнопками и меню
"""

import os
import logging
import json
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
        return {
            "subjects": [],
            "schedule": {},
            "messages_count": 0,
            "users": {}
        }

def save_data(data):
    """Сохранить данные в файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Создание клавиатур
def get_main_menu_keyboard():
    """Главное меню"""
    keyboard = [
        [InlineKeyboardButton("📚 Предметы", callback_data="menu:subjects")],
        [InlineKeyboardButton("📅 Расписание", callback_data="menu:schedule")],
        [InlineKeyboardButton("➕ Добавить предмет", callback_data="menu:add_subject")],
        [InlineKeyboardButton("📊 Статистика", callback_data="menu:stats")],
        [InlineKeyboardButton("❓ Помощь", callback_data="menu:help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_subjects_keyboard(subjects):
    """Клавиатура предметов"""
    keyboard = []
    for i, subject in enumerate(subjects):
        keyboard.append([InlineKeyboardButton(f"📖 {subject}", callback_data=f"subject:{i}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back:main")])
    return InlineKeyboardMarkup(keyboard)

def get_schedule_keyboard():
    """Клавиатура расписания"""
    keyboard = [
        [InlineKeyboardButton("Понедельник", callback_data="day:monday")],
        [InlineKeyboardButton("Вторник", callback_data="day:tuesday")],
        [InlineKeyboardButton("Среда", callback_data="day:wednesday")],
        [InlineKeyboardButton("Четверг", callback_data="day:thursday")],
        [InlineKeyboardButton("Пятница", callback_data="day:friday")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back:main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_day_keyboard(day):
    """Клавиатура для дня недели"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить предмет", callback_data=f"edit:{day}:add")],
        [InlineKeyboardButton("✏️ Редактировать", callback_data=f"edit:{day}:edit")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back:schedule")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    data = load_data()
    
    # Сохраняем информацию о пользователе
    if "users" not in data:
        data["users"] = {}
    
    data["users"][str(user_id)] = {
        "username": update.effective_user.username,
        "first_name": update.effective_user.first_name,
        "last_name": update.effective_user.last_name
    }
    save_data(data)
    
    await update.message.reply_text(
        "🤖 Добро пожаловать в бот управления расписанием!\n\n"
        "Выберите действие из меню ниже:",
        reply_markup=get_main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📚 Доступные команды:

/start - Начать работу с ботом
/help - Показать эту справку

🎯 Основные функции:
• 📚 Управление предметами
• 📅 Просмотр расписания
• ➕ Добавление новых предметов
• 📊 Статистика использования

💡 Используйте кнопки меню для навигации!
"""
    await update.message.reply_text(help_text)

# Обработчики callback запросов
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик главного меню"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(":")[1]
    
    if data == "subjects":
        subjects = load_data().get("subjects", [])
        if not subjects:
            await query.edit_message_text(
                "📝 Список предметов пуст.\nИспользуйте кнопку 'Добавить предмет' для создания нового предмета.",
                reply_markup=get_subjects_keyboard([])
            )
        else:
            await query.edit_message_text(
                "📚 Выберите предмет:",
                reply_markup=get_subjects_keyboard(subjects)
            )
    
    elif data == "schedule":
        await query.edit_message_text(
            "📅 Выберите день недели:",
            reply_markup=get_schedule_keyboard()
        )
    
    elif data == "add_subject":
        await query.edit_message_text(
            "➕ Введите название нового предмета:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back:main")]])
        )
        context.user_data["waiting_for_subject"] = True
    
    elif data == "stats":
        data_obj = load_data()
        subjects_count = len(data_obj.get("subjects", []))
        messages_count = data_obj.get("messages_count", 0)
        users_count = len(data_obj.get("users", {}))
        
        await query.edit_message_text(
            f"📊 Статистика бота:\n\n"
            f"📚 Предметов: {subjects_count}\n"
            f"💬 Сообщений: {messages_count}\n"
            f"👥 Пользователей: {users_count}\n"
            f"🏠 Хостинг: Timeweb",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back:main")]])
        )
    
    elif data == "help":
        await query.edit_message_text(
            "❓ Помощь:\n\n"
            "📚 Предметы - просмотр и управление предметами\n"
            "📅 Расписание - просмотр расписания по дням\n"
            "➕ Добавить предмет - создание нового предмета\n"
            "📊 Статистика - информация о боте\n\n"
            "💡 Используйте кнопки для навигации!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back:main")]])
        )

async def subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора предмета"""
    query = update.callback_query
    await query.answer()
    
    subject_index = int(query.data.split(":")[1])
    data = load_data()
    subjects = data.get("subjects", [])
    
    if subject_index < len(subjects):
        subject = subjects[subject_index]
        keyboard = [
            [InlineKeyboardButton("✏️ Редактировать", callback_data=f"edit_subject:{subject_index}")],
            [InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_subject:{subject_index}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back:subjects")]
        ]
        
        await query.edit_message_text(
            f"📖 Предмет: {subject}\n\n"
            f"Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def day_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора дня недели"""
    query = update.callback_query
    await query.answer()
    
    day = query.data.split(":")[1]
    day_names = {
        "monday": "Понедельник",
        "tuesday": "Вторник", 
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница"
    }
    
    day_name = day_names.get(day, day)
    data = load_data()
    schedule = data.get("schedule", {})
    day_subjects = schedule.get(day, [])
    
    if not day_subjects:
        text = f"📅 {day_name}\n\nРасписание пусто."
    else:
        text = f"📅 {day_name}\n\nПредметы:\n" + "\n".join(f"• {subject}" for subject in day_subjects)
    
    await query.edit_message_text(
        text,
        reply_markup=get_day_keyboard(day)
    )

async def edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик редактирования"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split(":")
    if len(parts) >= 3:
        action_type = parts[1]
        action = parts[2]
        
        if action_type == "add":
            await query.edit_message_text(
                f"➕ Добавить предмет в {action}:\n\nВведите название предмета:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data=f"back:day:{action}")]])
            )
            context.user_data["waiting_for_day_subject"] = action
        elif action_type == "edit":
            await query.edit_message_text(
                f"✏️ Редактирование расписания для {action}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data=f"back:day:{action}")]])
            )

async def back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Назад'"""
    query = update.callback_query
    await query.answer()
    
    back_to = query.data.split(":")[1]
    
    if back_to == "main":
        await query.edit_message_text(
            "🤖 Главное меню:\n\nВыберите действие:",
            reply_markup=get_main_menu_keyboard()
        )
    elif back_to == "subjects":
        data = load_data()
        subjects = data.get("subjects", [])
        await query.edit_message_text(
            "📚 Выберите предмет:",
            reply_markup=get_subjects_keyboard(subjects)
        )
    elif back_to == "schedule":
        await query.edit_message_text(
            "📅 Выберите день недели:",
            reply_markup=get_schedule_keyboard()
        )

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_text = update.message.text
    
    # Увеличиваем счетчик сообщений
    data = load_data()
    data["messages_count"] = data.get("messages_count", 0) + 1
    
    # Проверяем, ждем ли мы ввод предмета
    if context.user_data.get("waiting_for_subject"):
        # Добавляем новый предмет
        if "subjects" not in data:
            data["subjects"] = []
        
        data["subjects"].append(user_text)
        save_data(data)
        
        await update.message.reply_text(
            f"✅ Предмет '{user_text}' добавлен!",
            reply_markup=get_main_menu_keyboard()
        )
        context.user_data["waiting_for_subject"] = False
    
    elif context.user_data.get("waiting_for_day_subject"):
        # Добавляем предмет в день недели
        day = context.user_data["waiting_for_day_subject"]
        if "schedule" not in data:
            data["schedule"] = {}
        if day not in data["schedule"]:
            data["schedule"][day] = []
        
        data["schedule"][day].append(user_text)
        save_data(data)
        
        await update.message.reply_text(
            f"✅ Предмет '{user_text}' добавлен в расписание!",
            reply_markup=get_main_menu_keyboard()
        )
        context.user_data["waiting_for_day_subject"] = None
    
    else:
        # Обычное эхо-сообщение
        save_data(data)
        await update.message.reply_text(
            f"💬 Вы написали: {user_text}\n\nИспользуйте /start для открытия главного меню.",
            reply_markup=get_main_menu_keyboard()
        )

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
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Добавляем обработчики callback запросов
    application.add_handler(CallbackQueryHandler(menu_callback, pattern=r"^menu:"))
    application.add_handler(CallbackQueryHandler(subject_callback, pattern=r"^subject:"))
    application.add_handler(CallbackQueryHandler(day_callback, pattern=r"^day:"))
    application.add_handler(CallbackQueryHandler(edit_callback, pattern=r"^edit:"))
    application.add_handler(CallbackQueryHandler(back_callback, pattern=r"^back:"))
    
    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo_message))
    
    # Запускаем бота
    logging.info("Bot is starting...")
    try:
        application.run_polling(close_loop=False, drop_pending_updates=True)
    except Exception as e:
        logging.error(f"Bot error: {e}")

if __name__ == "__main__":
    main()
