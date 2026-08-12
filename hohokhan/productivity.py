from __future__ import annotations

import re

NOTE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_\-\u0600-\u06FF]{1,32}$")


def format_duration(total_seconds: int) -> str:
    total_seconds = max(0, total_seconds)
    days, remainder = divmod(total_seconds, 86_400)
    hours, remainder = divmod(remainder, 3_600)
    minutes, seconds = divmod(remainder, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days} روز")
    if hours:
        parts.append(f"{hours} ساعت")
    if minutes:
        parts.append(f"{minutes} دقیقه")
    if not parts:
        parts.append(f"{seconds} ثانیه")
    return " و ".join(parts[:2])


def normalize_note_name(value: str) -> str:
    name = value.strip()
    if not NOTE_NAME_PATTERN.fullmatch(name):
        raise ValueError("نام یادداشت باید ۱ تا ۳۲ نویسه و شامل حرف، عدد، _ یا - باشد")
    return name
