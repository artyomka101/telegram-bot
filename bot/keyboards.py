from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from bot.data import DAY_LABELS, SUBJECTS, get_all_day_keys


def build_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Обычная клавиатура с кнопками внизу экрана"""
    buttons = [
        [KeyboardButton(text="📚 Предметы"), KeyboardButton(text="📅 Расписание по дню")],
        [KeyboardButton(text="📝 ДЗ на завтра")],
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="⚙️ Админ")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def build_main_menu_inline_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Inline кнопки под сообщением (старая версия)"""
    buttons = [
        [InlineKeyboardButton(text="📚 Предметы", callback_data="menu:subjects")],
        [InlineKeyboardButton(text="📅 Расписание по дню", callback_data="menu:day")],
        [InlineKeyboardButton(text="📝 ДЗ на завтра", callback_data="menu:tomorrow")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="⚙️ Админ", callback_data="menu:admin")])
    return InlineKeyboardMarkup(buttons)


def build_subjects_keyboard() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for subject in SUBJECTS.values():
        row.append(InlineKeyboardButton(text=subject.name, callback_data=f"subject:{subject.key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back:main")])
    return InlineKeyboardMarkup(rows)


def build_days_keyboard() -> InlineKeyboardMarkup:
    # Показать только реально существующие дни в расписании, в предсказуемом порядке
    from bot.data import SCHEDULE  # локальный импорт

    all_keys = get_all_day_keys()
    present = [dk for dk in all_keys if dk in SCHEDULE]
    # доб. любые нестандартные ключи в конец
    extra = [dk for dk in SCHEDULE.keys() if dk not in present]
    day_keys = present + extra

    rows = []
    row = []
    for dk in day_keys:
        row.append(InlineKeyboardButton(text=DAY_LABELS.get(dk, dk), callback_data=f"day:{dk}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back:main")])
    return InlineKeyboardMarkup(rows)


def build_admin_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="✏️ Ред. ДЗ", callback_data="menu:edit_hw")],
        [InlineKeyboardButton(text="🗓️ Ред. расписание", callback_data="menu:edit_sched")],
        [InlineKeyboardButton(text="📆 Управление днями", callback_data="menu:days_manage")],
        [InlineKeyboardButton(text="🔤 Переименовать предмет", callback_data="menu:rename_subj")],
        [InlineKeyboardButton(text="➕ Новый предмет (в базу)", callback_data="menu:add_subject")],
        [InlineKeyboardButton(text="🗑️ Удалить предмет", callback_data="menu:del_subject")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back:main")],
    ]
    return InlineKeyboardMarkup(buttons)


def build_back_to_main_only_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="⬅️ Назад", callback_data="back:main")]]
    )


def build_manage_days_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text="➕ Создать день", callback_data="menu:days_manage:create")],
        [InlineKeyboardButton(text="🗑️ Удалить день", callback_data="menu:days_manage:delete")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:admin")],
    ])


def build_days_choice_keyboard(prefix: str, keys: list[str]) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for dk in keys:
        row.append(InlineKeyboardButton(text=DAY_LABELS.get(dk, dk), callback_data=f"{prefix}{dk}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:days_manage")])
    return InlineKeyboardMarkup(rows)


def build_days_to_create_keyboard() -> InlineKeyboardMarkup:
    from bot.data import SCHEDULE  # локальный импорт

    all_keys = get_all_day_keys()
    missing = [dk for dk in all_keys if dk not in SCHEDULE]
    return build_days_choice_keyboard("edit:days:create:", missing)


def build_days_to_delete_keyboard() -> InlineKeyboardMarkup:
    from bot.data import SCHEDULE  # локальный импорт

    present = list(SCHEDULE.keys())
    # Порядок по all_keys, а затем остальные
    all_keys = get_all_day_keys()
    ordered = [dk for dk in all_keys if dk in present] + [dk for dk in present if dk not in all_keys]
    return build_days_choice_keyboard("edit:days:delete:", ordered)


def build_subjects_keyboard_with_prefix(prefix: str) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for subject in SUBJECTS.values():
        row.append(InlineKeyboardButton(text=subject.name, callback_data=f"{prefix}{subject.key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back:main")])
    return InlineKeyboardMarkup(rows)


def build_subjects_keyboard_for_day_add(day_key: str) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for subject in SUBJECTS.values():
        row.append(InlineKeyboardButton(text=subject.name, callback_data=f"edit:sched:add:{subject.key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="🧹 Очистить день", callback_data="edit:sched:days:clear")])
    rows.append([InlineKeyboardButton(text="⬅️ К выбору дня", callback_data="menu:edit_sched")])
    return InlineKeyboardMarkup(rows)


def build_days_keyboard_with_prefix(prefix: str) -> InlineKeyboardMarkup:
    # Аналогично build_days_keyboard — показываем существующие дни первыми
    from bot.data import SCHEDULE  # локальный импорт

    all_keys = get_all_day_keys()
    present = [dk for dk in all_keys if dk in SCHEDULE]
    extra = [dk for dk in SCHEDULE.keys() if dk not in present]
    day_keys = present + extra
    rows = []
    row = []
    for dk in day_keys:
        row.append(InlineKeyboardButton(text=DAY_LABELS.get(dk, dk), callback_data=f"{prefix}{dk}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back:main")])
    return InlineKeyboardMarkup(rows)


def build_edit_schedule_actions_keyboard(day_key: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="📚 Выбрать предмет", callback_data="edit:sched:add")],
        [InlineKeyboardButton(text="✏️ Редактировать урок", callback_data="edit:sched:edit")],
        [InlineKeyboardButton(text="➖ Удалить предмет", callback_data="edit:sched:del")],
        [InlineKeyboardButton(text="🧹 Очистить день", callback_data="edit:sched:days:clear")],
        [InlineKeyboardButton(text="⬅️ К выбору дня", callback_data="menu:edit_sched")],
    ]
    return InlineKeyboardMarkup(rows)


def build_edit_lessons_keyboard(day_key: str) -> InlineKeyboardMarkup:
    from bot.data import SCHEDULE, SUBJECTS  # локальный импорт, чтобы избежать циклов

    lessons = SCHEDULE.get(day_key, [])
    rows = []
    row = []
    for i, subject_key in enumerate(lessons, 1):
        subject = SUBJECTS.get(subject_key)
        subject_name = subject.name if subject else f"Неизвестный предмет ({subject_key})"
        row.append(InlineKeyboardButton(text=f"{i}. {subject_name}", callback_data=f"edit:sched:edit_choose:{i}"))
        if len(row) == 1:  # По одному уроку в ряд для удобства
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"edit:sched:day:{day_key}")])
    return InlineKeyboardMarkup(rows)


def build_delete_indices_keyboard(day_key: str) -> InlineKeyboardMarkup:
    from bot.data import SCHEDULE  # локальный импорт, чтобы избежать циклов

    indices = list(range(1, len(SCHEDULE.get(day_key, [])) + 1))
    rows = []
    row = []
    for i in indices:
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"edit:sched:del_choose:{i}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"edit:sched:day:{day_key}")])
    return InlineKeyboardMarkup(rows)



