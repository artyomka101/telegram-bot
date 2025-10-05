from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest

from bot.data import (
    get_schedule_for_day,
    get_subject_by_key,
    get_tomorrow_day_key,
    get_day_label,
    SUBJECTS,
    Subject,
    SCHEDULE,
)
from bot.keyboards import (
    build_main_menu_keyboard,
    build_subjects_keyboard,
    build_days_keyboard,
    build_subjects_keyboard_with_prefix,
    build_days_keyboard_with_prefix,
    build_edit_schedule_actions_keyboard,
    build_edit_lessons_keyboard,
    build_delete_indices_keyboard,
    build_admin_menu_keyboard,
    build_back_to_main_only_keyboard,
    build_manage_days_keyboard,
    build_days_to_create_keyboard,
    build_days_to_delete_keyboard,
    build_subjects_keyboard_for_day_add,
)
from bot.storage import load_data, save_data
from bot.config import get_settings


async def safe_edit_message(query, text: str, reply_markup=None):
    """Безопасное редактирование сообщения с обработкой ошибки 'Message is not modified'"""
    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    except BadRequest as e:
        if "Message is not modified" in str(e):
            # Сообщение не изменилось, просто отвечаем
            await query.answer("✓")
        else:
            # Другая ошибка, пробрасываем дальше
            raise


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.effective_user.first_name if update.effective_user else ""
    greeting = (
        "Привет! Я твой Telegram-бот.\n"
        "- Отправь любое сообщение — я его повторю.\n"
        "- Используй /help, чтобы узнать команды."
    )
    if user_first_name:
        greeting = f"Привет, {user_first_name}!\n\n" + greeting

    await update.message.reply_text(
        greeting,
        reply_markup=build_main_menu_keyboard(is_admin=_is_admin(update)),
    )  # type: ignore[union-attr]


async def admin_reload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    if settings.admin_user_id and update.effective_user and update.effective_user.id != settings.admin_user_id:
        await update.message.reply_text("Эта команда только для админа")  # type: ignore[union-attr]
        return
    load_data()
    await update.message.reply_text("Данные перезагружены из data.json")  # type: ignore[union-attr]


async def admin_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    if settings.admin_user_id and update.effective_user and update.effective_user.id != settings.admin_user_id:
        await update.message.reply_text("Эта команда только для админа")  # type: ignore[union-attr]
        return
    save_data()
    await update.message.reply_text("Данные сохранены в data.json")  # type: ignore[union-attr]


def _is_admin(update: Update) -> bool:
    settings = get_settings()
    if not settings.admin_user_id:
        return True  # если админ не задан, считаем что доступ открыт
    if not update.effective_user:
        return False
    return update.effective_user.id == settings.admin_user_id


async def _send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    markup = build_main_menu_keyboard(is_admin=_is_admin(update))
    query = update.callback_query
    if query and query.message:
        await query.message.reply_text(text, reply_markup=markup)
    elif update.message:
        await update.message.reply_text(text, reply_markup=markup)


def _slugify_key(name: str) -> str:
    mapping = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d",
        "е": "e", "ё": "e", "ж": "zh", "з": "z", "и": "i",
        "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
        "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
        "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "ch",
        "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "",
        "э": "e", "ю": "yu", "я": "ya",
    }
    s = name.strip().lower()
    res_chars: list[str] = []
    for ch in s:
        if ch in mapping:
            res_chars.append(mapping[ch])
        elif ch.isalnum():
            res_chars.append(ch)
        elif ch in [" ", "-", "/", "\\", ",", ".", ":", ";", "(", ")"]:
            res_chars.append("_")
        # else: skip other symbols
    key = "".join(res_chars)
    key = "_".join(filter(None, key.split("_")))  # collapse repeats
    key = key.strip("_")
    return key or "subj"


def _make_unique_key(base_key: str) -> str:
    key = base_key
    idx = 2
    while key in SUBJECTS:
        key = f"{base_key}_{idx}"
        idx += 1
    return key


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Доступные команды:\n"
        "/start — приветствие и краткая справка\n"
        "/help — показать эту помощь\n\n"
        "Просто отправь текст — я повторю его в ответ."
    )
    await update.message.reply_text(
        help_text,
        reply_markup=build_main_menu_keyboard(is_admin=_is_admin(update)),
    )  # type: ignore[union-attr]


async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Перехват текстов, если ожидается ввод нового ДЗ
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user_data = context.user_data
    
    # Обработка нажатий на кнопки главного меню
    if text == "📚 Предметы":
        await update.message.reply_text(
            "Выбери предмет:", 
            reply_markup=build_subjects_keyboard()
        )
        return
    elif text == "📅 Расписание по дню":
        await update.message.reply_text(
            "Выбери день недели:", 
            reply_markup=build_days_keyboard()
        )
        return
    elif text == "📝 ДЗ на завтра":
        day_key = get_tomorrow_day_key()
        day_label = get_day_label(day_key)
        schedule = get_schedule_for_day(day_key)
        if not schedule:
            text_msg = f"На {day_label} занятий нет."
        else:
            lines = [f"ДЗ на завтра ({day_label}):"]
            for order, subject in schedule:
                lines.append(f"{order}. <b>{subject.name}</b>: {subject.homework}")
            text_msg = "\n".join(lines)
        await update.message.reply_text(
            text_msg,
            reply_markup=build_main_menu_keyboard(is_admin=_is_admin(update)),
            parse_mode=ParseMode.HTML,
        )
        return
    elif text == "⚙️ Админ":
        if not _is_admin(update):
            await update.message.reply_text("Только для админа")
            return
        await update.message.reply_text(
            "Админ-панель:", 
            reply_markup=build_admin_menu_keyboard()
        )
        return
    
    pending_subject_key: str | None = user_data.get("edit_hw_subject")  # type: ignore[assignment]
    if pending_subject_key:
        if not _is_admin(update):
            await update.message.reply_text("Редактирование доступно только админу.", reply_markup=build_main_menu_keyboard())
            user_data.pop("edit_hw_subject", None)
            return

        subject = SUBJECTS.get(pending_subject_key)
        if not subject:
            await update.message.reply_text("Неизвестный предмет.", reply_markup=build_main_menu_keyboard())
            user_data.pop("edit_hw_subject", None)
            return

        new_hw = update.message.text.strip()
        SUBJECTS[pending_subject_key] = Subject(key=subject.key, name=subject.name, homework=new_hw)
        save_data()
        await _send_main_menu(update, context, f"ДЗ для {subject.name} обновлено.")
        user_data.pop("edit_hw_subject", None)
        return

    # Переименование предмета
    rename_key: str | None = user_data.get("rename_subject_key")  # type: ignore[assignment]
    if rename_key:
        if not _is_admin(update):
            await update.message.reply_text("Переименование доступно только админу.", reply_markup=build_main_menu_keyboard())
            user_data.pop("rename_subject_key", None)
            return
        subject = SUBJECTS.get(rename_key)
        if not subject:
            await update.message.reply_text("Неизвестный предмет.", reply_markup=build_main_menu_keyboard())
            user_data.pop("rename_subject_key", None)
            return
        new_name = update.message.text.strip()
        # Обновляем только имя, ключ остаётся прежним
        SUBJECTS[rename_key] = Subject(key=subject.key, name=new_name, homework=subject.homework)
        save_data()
        await _send_main_menu(update, context, f"Название предмета обновлено: {subject.name} → {new_name}")
        user_data.pop("rename_subject_key", None)
        return

    # Обычный эхо-ответ
    # Перехват добавления нового предмета
    if user_data.get("await_new_subject") or user_data.get("await_new_subject_simple"):
        if not _is_admin(update):
            await update.message.reply_text("Добавление доступно только админу.", reply_markup=build_back_to_main_only_keyboard())
            user_data.pop("await_new_subject", None)
            user_data.pop("await_new_subject_simple", None)
            return
        raw = update.message.text.strip()
        if user_data.get("await_new_subject"):
            parts = [p.strip() for p in raw.split(";")]
            if len(parts) < 2:
                await update.message.reply_text(
                    "Неверный формат. Нужно: ключ;название;дз (дз можно пустым)",
                    reply_markup=build_back_to_main_only_keyboard(),
                )
                user_data.pop("await_new_subject", None)
                user_data.pop("await_new_subject_simple", None)
                return
            key = parts[0]
            name = parts[1]
            hw = parts[2] if len(parts) >= 3 else ""
        else:
            # Простой формат: "Название" или "Название: ДЗ"
            if ":" in raw:
                name, hw = [p.strip() for p in raw.split(":", 1)]
            else:
                name, hw = raw, ""
            key = _make_unique_key(_slugify_key(name))
        if not key or not name:
            await update.message.reply_text("Ключ и название обязательны.", reply_markup=build_back_to_main_only_keyboard())
            user_data.pop("await_new_subject", None)
            user_data.pop("await_new_subject_simple", None)
            return
        if key in SUBJECTS:
            await update.message.reply_text("Такой ключ уже существует.", reply_markup=build_back_to_main_only_keyboard())
            user_data.pop("await_new_subject", None)
            user_data.pop("await_new_subject_simple", None)
            return
        SUBJECTS[key] = Subject(key=key, name=name, homework=hw)
        save_data()
        await _send_main_menu(update, context, f"Предмет добавлен: {name} (ключ: {key})")
        user_data.pop("await_new_subject", None)
        user_data.pop("await_new_subject_simple", None)
        return

        await update.message.reply_text(update.message.text)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Неизвестная команда. Попробуй /help",
        reply_markup=build_main_menu_keyboard(is_admin=_is_admin(update)),
    )  # type: ignore[union-attr]


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    data = query.data or ""

    if data == "menu:admin":
        if not _is_admin(update):
            await query.answer("Только для админа")
            return
        await query.edit_message_text(
            text="Админ-панель:", reply_markup=build_admin_menu_keyboard()
        )
    elif data == "menu:subjects":
        await query.edit_message_text(
            text="Выбери предмет:", reply_markup=build_subjects_keyboard()
        )
    elif data == "menu:day":
        await query.edit_message_text(
            text="Выбери день недели:", reply_markup=build_days_keyboard()
        )
    elif data == "menu:tomorrow":
        day_key = get_tomorrow_day_key()
        day_label = get_day_label(day_key)
        schedule = get_schedule_for_day(day_key)
        if not schedule:
            text = f"На {day_label} занятий нет."
        else:
            lines = [f"ДЗ на завтра ({day_label}):"]
            for order, subject in schedule:
                lines.append(f"{order}. <b>{subject.name}</b>: {subject.homework}")
            text = "\n".join(lines)
        await query.edit_message_text(
            text=text,
            reply_markup=build_main_menu_keyboard(is_admin=_is_admin(update)),
            parse_mode=ParseMode.HTML,
        )
    elif data == "menu:edit_hw":
        if not _is_admin(update):
            await query.answer("Только для админа")
            return
        await query.edit_message_text(
            text="Выбери предмет для изменения ДЗ:",
            reply_markup=build_subjects_keyboard_with_prefix("edit:hw:"),
        )
    elif data == "menu:edit_sched":
        if not _is_admin(update):
            await query.answer("Только для админа")
            return
        await query.edit_message_text(
            text="Выбери день для редактирования расписания:",
            reply_markup=build_days_keyboard_with_prefix("edit:sched:day:"),
        )
    elif data == "menu:rename_subj":
        if not _is_admin(update):
            await query.answer("Только для админа")
            return
        await query.edit_message_text(
            text="Выбери предмет для переименования:",
            reply_markup=build_subjects_keyboard_with_prefix("edit:rename:"),
        )
    elif data == "menu:add_subject":
        if not _is_admin(update):
            await query.answer("Только для админа")
            return
        await query.edit_message_text(
            text=(
                "Отправь новым сообщением название предмета.\n"
                "Можно добавить ДЗ через двоеточие: 'Название: ДЗ'.\n"
                "Ключ сгенерируется автоматически."
            ),
            reply_markup=build_back_to_main_only_keyboard(),
        )
        context.user_data["await_new_subject_simple"] = True
    elif data == "menu:days_manage":
        if not _is_admin(update):
            await query.answer("Только для админа")
            return
        await query.edit_message_text(
            text="Управление днями:",
            reply_markup=build_manage_days_keyboard(),
        )
    elif data == "menu:days_manage:create":
        if not _is_admin(update):
            await query.answer("Только для админа")
            return
        await query.edit_message_text(
            text="Выбери день для создания:",
            reply_markup=build_days_to_create_keyboard(),
        )
    elif data == "menu:days_manage:delete":
        if not _is_admin(update):
            await query.answer("Только для админа")
            return
        await query.edit_message_text(
            text="Выбери день для удаления:",
            reply_markup=build_days_to_delete_keyboard(),
        )
    elif data == "menu:del_subject":
        if not _is_admin(update):
            await query.answer("Только для админа")
            return
        await query.edit_message_text(
            text="Выбери предмет для удаления:",
            reply_markup=build_subjects_keyboard_with_prefix("edit:del_subj:"),
        )


async def subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    data = query.data or ""
    if not data.startswith("subject:"):
        return
    key = data.split(":", 1)[1]
    subject = get_subject_by_key(key)
    if not subject:
        await query.answer("Неизвестный предмет")
        return

    # Найти дни, когда есть предмет
    from bot.data import get_days_for_subject

    days = get_days_for_subject(key)
    schedule_text = "\n".join([f"- {day} (урок {order})" for day, order in days]) or "—"
    text = (
        f"<b>{subject.name}</b>\n"
        f"ДЗ: {subject.homework}\n\n"
        f"Ближайшие занятия:\n{schedule_text}"
    )
    await query.edit_message_text(
        text=text, reply_markup=build_subjects_keyboard(), parse_mode=ParseMode.HTML
    )


async def day_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    data = query.data or ""
    if not data.startswith("day:"):
        return
    day_key = data.split(":", 1)[1]
    day_label = get_day_label(day_key)
    schedule = get_schedule_for_day(day_key)
    if not schedule:
        text = f"На {day_label} занятий нет."
    else:
        lines = [f"Расписание на {day_label}:"]
        for order, subject in schedule:
            lines.append(f"{order}. {subject.name}")
        text = "\n".join(lines)

    await query.edit_message_text(
        text=text, reply_markup=build_days_keyboard()
    )


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    # Удаляем старое сообщение с inline-кнопками
    try:
        await query.message.delete()
    except:
        pass
    # Отправляем новое сообщение с reply-клавиатурой
    await query.message.reply_text(
        text="Главное меню:", 
        reply_markup=build_main_menu_keyboard(is_admin=_is_admin(update))
    )
    await query.answer()


def _render_day_schedule(day_key: str) -> str:
    day_label = get_day_label(day_key)
    schedule = get_schedule_for_day(day_key)
    if not schedule:
        return f"Редактирование расписания: {day_label}\nНа {day_label} занятий нет."
    lines = [f"Редактирование расписания: {day_label}"]
    for order, subject in schedule:
        lines.append(f"{order}. {subject.name}")
    return "\n".join(lines)


async def edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    raw = query.data or ""
    data = raw.split(":")
    raw_lc = raw.lower()
    if not _is_admin(update):
        await query.answer("Только для админа")
        return

    # Patterns:
    # edit:hw:<subject_key>
    # edit:rename:<subject_key>
    # edit:del_subj:<subject_key>
    # edit:sched:day:<day_key>
    # edit:sched:add:<day_key>
    # edit:sched:add:<day_key>:<subject_key>
    # edit:sched:del:<day_key>
    # edit:sched:del:<day_key>:<index>
    # edit:sched:clear:<day_key>
    # edit:days:create:<day_key>
    # edit:days:delete:<day_key>

    # Backward/defensive handling for possible stale buttons
    if raw in ("edit:add_subject", "edit:create_subject") or (
        ("add" in raw_lc or "create" in raw_lc) and ("subj" in raw_lc or "subject" in raw_lc)
    ):
        await query.edit_message_text(
            text=(
                "Отправь новым сообщением название предмета.\n"
                "Можно добавить ДЗ через двоеточие: 'Название: ДЗ'.\n"
                "Ключ сгенерируется автоматически."
            ),
            reply_markup=build_back_to_main_only_keyboard(),
        )
        context.user_data["await_new_subject_simple"] = True
        return

    # Fast-path: adding subject directly edit:sched:add:<subject_key>
    if raw.startswith("edit:sched:add:") and len(data) == 4:
        day_key = context.user_data.get("edit_sched_day")
        if not isinstance(day_key, str) or not day_key:
            await query.answer("Сначала выбери день")
            return
        subject_key = data[3]
        if subject_key not in SUBJECTS:
            await query.answer("Неизвестный предмет")
            return
        SCHEDULE.setdefault(day_key, []).append(subject_key)
        save_data()
        await query.answer("Добавлено")
        await safe_edit_message(
            query,
            text=_render_day_schedule(day_key),
            reply_markup=build_edit_schedule_actions_keyboard(day_key),
        )
        return

    # Fast-path: clear day edit:sched:days:clear
    if raw == "edit:sched:days:clear":
        day_key = context.user_data.get("edit_sched_day")
        if not isinstance(day_key, str) or not day_key:
            await query.answer("Сначала выбери день")
            return
        SCHEDULE[day_key] = []
        save_data()
        await safe_edit_message(
            query,
            text=_render_day_schedule(day_key),
            reply_markup=build_edit_schedule_actions_keyboard(day_key),
        )
        return

    # Fast-path: show subjects for adding edit:sched:add
    if raw == "edit:sched:add":
        day_key = context.user_data.get("edit_sched_day")
        if not isinstance(day_key, str) or not day_key:
            await query.answer("Сначала выбери день")
            return
        await query.edit_message_text(
            text="Выбери предмет для добавления:",
            reply_markup=build_subjects_keyboard_with_prefix("edit:sched:add:"),
        )
        return

    # Fast-path: show lessons for deletion edit:sched:del
    if raw == "edit:sched:del":
        day_key = context.user_data.get("edit_sched_day")
        if not isinstance(day_key, str) or not day_key:
            await query.answer("Сначала выбери день")
            return
        await query.edit_message_text(
            text="Выбери номер урока для удаления:",
            reply_markup=build_delete_indices_keyboard(day_key),
        )
        return

    # Fast-path: delete specific lesson edit:sched:del_choose:<index>
    if raw.startswith("edit:sched:del_choose:") and len(data) == 4:
        day_key = context.user_data.get("edit_sched_day")
        if not isinstance(day_key, str) or not day_key:
            await query.answer("Сначала выбери день")
            return
        try:
            idx = int(data[3])
        except ValueError:
            await query.answer("Неверный номер")
            return
        items = SCHEDULE.get(day_key, [])
        if 1 <= idx <= len(items):
            del items[idx - 1]
            save_data()
            await safe_edit_message(
                query,
                text=_render_day_schedule(day_key),
                reply_markup=build_edit_schedule_actions_keyboard(day_key),
            )
        return

    # Fast-path: show lessons for editing edit:sched:edit
    if raw == "edit:sched:edit":
        day_key = context.user_data.get("edit_sched_day")
        if not isinstance(day_key, str) or not day_key:
            await query.answer("Сначала выбери день")
            return
        await query.edit_message_text(
            text="Выбери урок для редактирования:",
            reply_markup=build_edit_lessons_keyboard(day_key),
        )
        return

    # Fast-path: edit specific lesson edit:sched:edit_choose:<index>
    if raw.startswith("edit:sched:edit_choose:") and len(data) == 4:
        day_key = context.user_data.get("edit_sched_day")
        if not isinstance(day_key, str) or not day_key:
            await query.answer("Сначала выбери день")
            return
        try:
            idx = int(data[3])
        except ValueError:
            await query.answer("Неверный номер")
            return
        items = SCHEDULE.get(day_key, [])
        if not (1 <= idx <= len(items)):
            await query.answer("Неверный номер урока")
            return
        
        # Сохраняем индекс для замены
        context.user_data["edit_lesson_index"] = idx - 1
        await query.edit_message_text(
            text="Выбери новый предмет для замены:",
            reply_markup=build_subjects_keyboard_with_prefix("edit:sched:replace:"),
        )
        return

    # Fast-path: replace lesson edit:sched:replace:<subject_key>
    if raw.startswith("edit:sched:replace:") and len(data) == 4:
        day_key = context.user_data.get("edit_sched_day")
        if not isinstance(day_key, str) or not day_key:
            await query.answer("Сначала выбери день")
            return
        lesson_idx = context.user_data.get("edit_lesson_index")
        if lesson_idx is None:
            await query.answer("Ошибка: не выбран урок")
            return
        subject_key = data[3]
        if subject_key not in SUBJECTS:
            await query.answer("Неизвестный предмет")
            return
        items = SCHEDULE.get(day_key, [])
        if 0 <= lesson_idx < len(items):
            # Проверяем, не тот же ли предмет
            if items[lesson_idx] == subject_key:
                await query.answer("Этот предмет уже установлен")
                return
            items[lesson_idx] = subject_key
            save_data()
            await query.answer("Урок изменён")
            await safe_edit_message(
                query,
                text=_render_day_schedule(day_key),
                reply_markup=build_edit_schedule_actions_keyboard(day_key),
            )
        else:
            await query.answer("Ошибка: неверный индекс урока")
        return

    if len(data) >= 2 and data[1] == "hw":
        if len(data) == 3:
            subject_key = data[2]
            subject = SUBJECTS.get(subject_key)
            if not subject:
                await query.answer("Неизвестный предмет")
                return
            context.user_data["edit_hw_subject"] = subject_key
            await query.edit_message_text(
                text=f"Введи новое ДЗ для {subject.name} сообщением.",
                reply_markup=build_back_to_main_only_keyboard(),
            )
        return

    if len(data) >= 2 and data[1] == "rename":
        if len(data) == 3:
            subject_key = data[2]
            subject = SUBJECTS.get(subject_key)
            if not subject:
                await query.answer("Неизвестный предмет")
                return
            context.user_data["rename_subject_key"] = subject_key
            await query.edit_message_text(
                text=f"Введи новое название для предмета: {subject.name}",
                reply_markup=build_back_to_main_only_keyboard(),
            )
        return

    if len(data) >= 2 and data[1] == "del_subj":
        if len(data) == 3:
            subject_key = data[2]
            subject = SUBJECTS.get(subject_key)
            if not subject:
                await query.answer("Неизвестный предмет")
                return
            # Удаляем из SUBJECTS и из всех дней расписания
            SUBJECTS.pop(subject_key, None)
            for dk, keys in list(SCHEDULE.items()):
                SCHEDULE[dk] = [k for k in keys if k != subject_key]
            save_data()
            await _send_main_menu(update, context, f"Предмет '{subject.name}' удалён, расписание обновлено.")
        return

    # Fast-path: select day for editing schedule → сразу показать выбор предметов
    if raw.startswith("edit:sched:day:"):
        parts = raw.split(":", 3)
        if len(parts) >= 4:
            day_key = parts[3]
            context.user_data["edit_sched_day"] = day_key
            await query.edit_message_text(
                text=f"Выбери предмет для добавления в {get_day_label(day_key)}:",
                reply_markup=build_subjects_keyboard_for_day_add(day_key),
            )
            return

    if len(data) >= 2 and data[1] == "sched":
        action = data[2] if len(data) >= 3 else ""
        if action == "day" and len(data) >= 4:
            day_key = data[3]
            # Сохраняем выбранный день и сразу показываем список предметов для добавления
            context.user_data["edit_sched_day"] = day_key
            await query.edit_message_text(
                text=f"Выбери предмет для добавления в {get_day_label(day_key)}:",
                reply_markup=build_subjects_keyboard_for_day_add(day_key),
            )
            return

    if len(data) >= 2 and data[1] == "days":
        action = data[2] if len(data) >= 3 else ""
        if action == "create" and len(data) == 4:
            dk = data[3]
            if dk not in SCHEDULE:
                SCHEDULE[dk] = []
                save_data()
            await _send_main_menu(update, context, f"День создан: {get_day_label(dk)}")
            return
        if action == "delete" and len(data) == 4:
            dk = data[3]
            if dk in SCHEDULE:
                del SCHEDULE[dk]
                save_data()
            await _send_main_menu(update, context, f"День удалён: {get_day_label(dk)}")
            return

        if action == "add":
            # Используем сохранённый день из состояния
            day_key = context.user_data.get("edit_sched_day")
            if not isinstance(day_key, str) or not day_key:
                await query.answer("Сначала выбери день")
                return
            # edit:sched:add → показать список предметов
            if len(data) == 3:
                await query.edit_message_text(
                    text="Выбери предмет для добавления:",
                    reply_markup=build_subjects_keyboard_with_prefix("edit:sched:add:"),
                )
                return
            # edit:sched:add:<subject_key> → добавить
            if len(data) == 4:
                subject_key = data[3]
                if subject_key not in SUBJECTS:
                    await query.answer("Неизвестный предмет")
                    return
                SCHEDULE.setdefault(day_key, []).append(subject_key)
                save_data()
                await query.answer("Добавлено")
                await query.edit_message_text(
                    text=_render_day_schedule(day_key),
                    reply_markup=build_edit_schedule_actions_keyboard(day_key),
                )
                return

        if action == "del":
            day_key = context.user_data.get("edit_sched_day")
            if not isinstance(day_key, str) or not day_key:
                await query.answer("Сначала выбери день")
                return
            if len(data) == 3:
                await query.edit_message_text(
                    text="Выбери номер урока для удаления:",
                    reply_markup=build_delete_indices_keyboard(day_key),
                )
                return
        if action == "del_choose" and len(data) == 4:
            day_key = context.user_data.get("edit_sched_day")
            if not isinstance(day_key, str) or not day_key:
                await query.answer("Сначала выбери день")
                return
            try:
                idx = int(data[3])
            except ValueError:
                await query.answer("Неверный номер")
                return
            items = SCHEDULE.get(day_key, [])
            if 1 <= idx <= len(items):
                del items[idx - 1]
                save_data()
            await query.edit_message_text(
                text=_render_day_schedule(day_key),
                reply_markup=build_edit_schedule_actions_keyboard(day_key),
            )
            return

        if action == "clear":
            day_key = context.user_data.get("edit_sched_day")
            if not isinstance(day_key, str) or not day_key:
                await query.answer("Сначала выбери день")
                return
            SCHEDULE[day_key] = []
            save_data()
            await query.edit_message_text(
                text=_render_day_schedule(day_key),
                reply_markup=build_edit_schedule_actions_keyboard(day_key),
            )
            return

    # fallback → показать админ-меню, чтобы обновить кнопки
    await query.edit_message_text(
        text="Админ-панель:", reply_markup=build_admin_menu_keyboard()
    )


