from __future__ import annotations

import re
import time
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


def find_downloaded_media(output_dir: Path, *, attempts: int = 5) -> Path:
    """Find yt-dlp's final media file after all post-processors have completed."""

    ignored_suffixes = {
        ".part",
        ".ytdl",
        ".json",
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }
    for attempt in range(attempts):
        candidates = [
            path
            for path in output_dir.rglob("*")
            if path.is_file()
            and path.suffix.casefold() not in ignored_suffixes
            and path.stat().st_size > 0
        ]
        if candidates:
            return max(candidates, key=lambda path: path.stat().st_mtime_ns)
        if attempt + 1 < attempts:
            time.sleep(0.2)
    raise FileNotFoundError(
        "فایل نهایی دانلود پیدا نشد؛ لاگ کانتینر را برای خطای yt-dlp یا ffmpeg بررسی کنید"
    )
