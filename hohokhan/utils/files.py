from __future__ import annotations

import re
from pathlib import Path

_UNSAFE_FILENAME = re.compile(r"[^\w\-.()\[\] ]+", re.UNICODE)


def safe_filename(value: str, fallback: str = "download") -> str:
    """Return a display-friendly filename without path traversal characters."""
    value = Path(value).name.replace("\x00", "").strip()
    value = _UNSAFE_FILENAME.sub("_", value).strip(" ._")
    return value[:180] or fallback


def human_bytes(value: int) -> str:
    size = float(value)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if size < 1024 or unit == "GiB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GiB"


def ensure_size(path: Path, maximum: int) -> None:
    size = path.stat().st_size
    if size > maximum:
        raise ValueError(f"file is too large ({human_bytes(size)})")
