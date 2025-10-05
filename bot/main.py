import logging

from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from bot.config import get_settings
from bot.storage import load_data
from bot.handlers import (
    echo_message,
    help_command,
    start,
    unknown_command,
    menu_callback,
    subject_callback,
    day_callback,
    back_to_main,
    admin_reload,
    admin_save,
    edit_callback,
)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    configure_logging()
    settings = get_settings()
    # Load persisted subjects/schedule from data.json on startup
    load_data()

    application = Application.builder().token(settings.bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reload", admin_reload))
    application.add_handler(CommandHandler("save", admin_save))

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo_message))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Inline кнопки/колбэки
    application.add_handler(CallbackQueryHandler(menu_callback, pattern=r"^menu:"))
    application.add_handler(CallbackQueryHandler(subject_callback, pattern=r"^subject:"))
    application.add_handler(CallbackQueryHandler(day_callback, pattern=r"^day:"))
    application.add_handler(CallbackQueryHandler(edit_callback, pattern=r"^edit:"))
    application.add_handler(CallbackQueryHandler(back_to_main, pattern=r"^back:main$"))

    application.run_polling(close_loop=False, drop_pending_updates=True)


if __name__ == "__main__":
    main()


