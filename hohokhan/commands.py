from __future__ import annotations

import re

_WEATHER_PREFIX = re.compile(
    r"^(?:\.weather|آب\s*و\s*هوای?|وضعیت\s+هوای?|هوای?)\s+",
    flags=re.IGNORECASE,
)
_ADMIN_SAY = re.compile(
    r"^هو\s*هو(?:\s*خان)?\s+بگو\s+(.+)$",
    flags=re.IGNORECASE | re.DOTALL,
)


def weather_city(text: str) -> str:
    city = _WEATHER_PREFIX.sub("", text.strip(), count=1).strip()
    if not city:
        raise ValueError("نام شهر را بنویسید")
    return city


def admin_say_text(text: str) -> str | None:
    match = _ADMIN_SAY.fullmatch(text.strip())
    if not match:
        return None
    value = match.group(1).strip()
    return value or None
