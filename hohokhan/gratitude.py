from __future__ import annotations

import re

_THANKS_RE = re.compile(
    r"(?:مرسی|ممنون(?:م|یم)?|متشکر(?:م|یم)?|سپاس(?:گزارم)?|تشکر|"
    r"دمت\s*گرم|دستت\s*درد\s*نکنه?|قربانت|قربونت)",
    flags=re.IGNORECASE,
)
_NAME_RE = re.compile(r"هو\s*هو(?:\s*خان)?", flags=re.IGNORECASE)


def normalize_persian(value: str) -> str:
    return (
        value.replace("ي", "ی")
        .replace("ك", "ک")
        .replace("\u200c", " ")
        .replace("\u200f", "")
        .replace("\u200e", "")
    )


def should_react_to_thanks(text: str, *, replies_to_self: bool) -> bool:
    normalized = normalize_persian(text)
    return bool(_THANKS_RE.search(normalized)) and (
        replies_to_self or bool(_NAME_RE.search(normalized))
    )
