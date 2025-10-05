from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Dict, List

from bot.data import Subject, SUBJECTS, SCHEDULE


DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


@dataclass
class SerializableSubject:
    key: str
    name: str
    homework: str


@dataclass
class SerializableData:
    subjects: List[SerializableSubject]
    schedule: Dict[str, List[str]]


def load_data() -> None:
    if not os.path.exists(DATA_FILE):
        save_data()  # создадим файл с текущими значениями
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError:
        return

    subs = raw.get("subjects", [])
    sched = raw.get("schedule", {})

    # Обновляем SUBJECTS/SCHEDULE in-place
    SUBJECTS.clear()
    for s in subs:
        key = s.get("key")
        name = s.get("name")
        hw = s.get("homework", "")
        if key and name:
            SUBJECTS[key] = Subject(key=key, name=name, homework=hw)

    SCHEDULE.clear()
    for day_key, subject_keys in sched.items():
        if isinstance(subject_keys, list):
            SCHEDULE[day_key] = [str(k) for k in subject_keys]


def save_data() -> None:
    subs = [SerializableSubject(key=s.key, name=s.name, homework=s.homework) for s in SUBJECTS.values()]
    data = SerializableData(
        subjects=subs,
        schedule=SCHEDULE,
    )
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(data), f, ensure_ascii=False, indent=2)



