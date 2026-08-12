from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # Allows config validation before optional packages are installed.

    def load_dotenv() -> bool:
        return False


class ConfigurationError(ValueError):
    """Raised when a required setting is absent or invalid."""


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.lower() == "replace_me":
        raise ConfigurationError(f"{name} is required")
    return value


def _integer(name: str, default: int | None = None, *, minimum: int = 1) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        if default is None:
            raise ConfigurationError(f"{name} is required")
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer") from exc
    if value < minimum:
        raise ConfigurationError(f"{name} must be at least {minimum}")
    return value


def _optional_integer(name: str) -> int | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer") from exc


def _optional_file(name: str) -> Path | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    path = Path(raw).expanduser().resolve()
    if not path.is_file():
        raise ConfigurationError(f"{name} must point to an existing file")
    return path


def _id_set(owner_id: int) -> frozenset[int]:
    values = {owner_id}
    raw = os.getenv("SUDO_USER_IDS", "")
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            values.add(int(item))
        except ValueError as exc:
            raise ConfigurationError("SUDO_USER_IDS must contain numeric IDs") from exc
    return frozenset(values)


@dataclass(frozen=True, slots=True)
class Settings:
    api_id: int
    api_hash: str
    session_name: str
    session_string: str | None
    owner_id: int
    sudo_user_ids: frozenset[int]
    data_dir: Path
    temp_dir: Path
    database_path: Path
    max_download_bytes: int
    max_media_duration_seconds: int
    download_concurrency: int
    rate_limit_messages: int
    rate_limit_window_seconds: int
    rate_limit_penalty_seconds: int
    openweather_api_key: str | None
    media_archive_chat_id: int | None
    ytdlp_cookies_file: Path | None
    ytdlp_sleep_interval_seconds: int
    log_level: str

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv()

        api_id = _integer("API_ID")
        api_hash = _required("API_HASH")
        owner_id = _integer("OWNER_ID")
        data_dir = Path(os.getenv("DATA_DIR", "./data")).expanduser().resolve()
        default_temp_dir = str(Path(tempfile.gettempdir()) / "hohokhan")
        temp_dir = Path(os.getenv("TEMP_DIR", default_temp_dir)).expanduser().resolve()
        max_download_mb = _integer("MAX_DOWNLOAD_MB", 150)

        return cls(
            api_id=api_id,
            api_hash=api_hash,
            session_name=os.getenv("SESSION_NAME", "hohokhan").strip() or "hohokhan",
            session_string=os.getenv("SESSION_STRING", "").strip() or None,
            owner_id=owner_id,
            sudo_user_ids=_id_set(owner_id),
            data_dir=data_dir,
            temp_dir=temp_dir,
            database_path=data_dir / "hohokhan.sqlite3",
            max_download_bytes=max_download_mb * 1024 * 1024,
            max_media_duration_seconds=_integer("MAX_MEDIA_DURATION_SECONDS", 1800),
            download_concurrency=_integer("DOWNLOAD_CONCURRENCY", 2),
            rate_limit_messages=_integer("RATE_LIMIT_MESSAGES", 8),
            rate_limit_window_seconds=_integer("RATE_LIMIT_WINDOW_SECONDS", 3),
            rate_limit_penalty_seconds=_integer("RATE_LIMIT_PENALTY_SECONDS", 300),
            openweather_api_key=os.getenv("OPENWEATHER_API_KEY", "").strip() or None,
            media_archive_chat_id=_optional_integer("MEDIA_ARCHIVE_CHAT_ID"),
            ytdlp_cookies_file=_optional_file("YTDLP_COOKIES_FILE"),
            ytdlp_sleep_interval_seconds=_integer(
                "YTDLP_SLEEP_INTERVAL_SECONDS", 5, minimum=0
            ),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
