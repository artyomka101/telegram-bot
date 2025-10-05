from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


# Ключи дней недели (ru): mon..sun
DayKey = str
SubjectKey = str


DAY_LABELS: Dict[DayKey, str] = {
    "mon": "Понедельник",
    "tue": "Вторник",
    "wed": "Среда",
    "thu": "Четверг",
    "fri": "Пятница",
    "sat": "Суббота",
    "sun": "Воскресенье",
}


@dataclass(frozen=True)
class Subject:
    key: SubjectKey
    name: str
    homework: str


# Статичный список предметов и ДЗ (пример — поменяйте под себя)
SUBJECTS: Dict[SubjectKey, Subject] = {
    "math": Subject("math", "Математика", "Решить задачи №1-10 на стр. 25"),
    "rus": Subject("rus", "Русский язык", "Упражнение 34, правило выучить"),
    "eng": Subject("eng", "Английский язык", "Выучить слова unit 3, упр. 5"),
    "cs": Subject("cs", "Информатика", "Подготовить файл с алгоритмом сортировки"),
    "hist": Subject("hist", "История", "Параграф 12, конспект"),
    "phys": Subject("phys", "Физика", "Задачи на законы Ньютона"),
    "chem": Subject("chem", "Химия", "§8, упр. после параграфа"),
    "bio": Subject("bio", "Биология", "Опорный конспект по теме клетки"),
    "lit": Subject("lit", "Литература", "Прочитать главу 4, краткий пересказ"),
    "geo": Subject("geo", "География", "Карта: обозначить материки и океаны"),
}


# Расписание: для каждого дня — список предметов по порядку уроков
# Время уроков можно не указывать; нумерация позиций даёт порядок
SCHEDULE: Dict[DayKey, List[SubjectKey]] = {
    "mon": ["math", "rus", "eng", "cs"],
    "tue": ["hist", "phys", "chem", "math"],
    "wed": ["bio", "lit", "eng"],
    "thu": ["geo", "rus", "math"],
    "fri": ["phys", "eng", "cs"],
    "sat": ["hist", "bio"],
    # "sun": []  # Обычно выходной
}


def list_subjects() -> List[Subject]:
    return list(SUBJECTS.values())


def get_subject_by_key(key: SubjectKey) -> Subject | None:
    return SUBJECTS.get(key)


def get_day_label(day_key: DayKey) -> str:
    return DAY_LABELS.get(day_key, day_key)


def get_schedule_for_day(day_key: DayKey) -> List[Tuple[int, Subject]]:
    keys = SCHEDULE.get(day_key, [])
    return [(idx + 1, SUBJECTS[k]) for idx, k in enumerate(keys) if k in SUBJECTS]


def get_days_for_subject(subject_key: SubjectKey) -> List[Tuple[str, int]]:
    result: List[Tuple[str, int]] = []
    for day_key, subjects in SCHEDULE.items():
        for idx, k in enumerate(subjects):
            if k == subject_key:
                result.append((get_day_label(day_key), idx + 1))
    return result


def get_all_day_keys() -> List[DayKey]:
    return ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def get_tomorrow_day_key(now: datetime | None = None) -> DayKey:
    dt = now or datetime.now()
    # weekday(): Monday=0..Sunday=6
    tomorrow = dt + timedelta(days=1)
    idx = tomorrow.weekday()  # 0..6
    mapping = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    return mapping[idx]



