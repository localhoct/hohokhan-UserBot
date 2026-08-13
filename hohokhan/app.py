from __future__ import annotations

import asyncio
import logging

from pyrogram import Client
from pyrogram.enums import ParseMode

from hohokhan.config import ConfigurationError, Settings
from hohokhan.database import Database
from hohokhan.rate_limit import RateLimiter


class HoHoKhanClient(Client):
    settings: Settings
    database: Database
    rate_limiter: RateLimiter
    download_semaphore: asyncio.Semaphore
    afk_notice_cache: dict[tuple[int, int], float]
    hafez_fortunes: dict[tuple[int, int], int]
    hafez_audio_messages: dict[int, int]
    hafez_audio_index_loaded: bool

    def __init__(self, settings: Settings) -> None:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        settings.temp_dir.mkdir(parents=True, exist_ok=True)

        super().__init__(
            name=settings.session_name,
            api_id=settings.api_id,
            api_hash=settings.api_hash,
            session_string=settings.session_string,
            in_memory=bool(settings.session_string),
            workdir=str(settings.data_dir),
            plugins={"root": "hohokhan.plugins"},
            parse_mode=ParseMode.HTML,
            workers=8,
            sleep_threshold=30,
        )
        self.settings = settings
        self.database = Database(settings.database_path)
        self.rate_limiter = RateLimiter(
            settings.rate_limit_messages,
            settings.rate_limit_window_seconds,
            settings.rate_limit_penalty_seconds,
        )
        self.download_semaphore = asyncio.Semaphore(settings.download_concurrency)
        self.afk_notice_cache = {}
        self.hafez_fortunes = {}
        self.hafez_audio_messages = {}
        self.hafez_audio_index_loaded = False

    async def start(
        self,
        *,
        use_qr: bool = False,
        except_ids: list[int] | None = None,
    ) -> HoHoKhanClient:
        await self.database.connect()
        try:
            await super().start(use_qr=use_qr, except_ids=except_ids or [])
        except Exception:
            await self.database.close()
            raise
        logging.getLogger(__name__).info("HoHoKhan started")
        return self

    async def stop(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        try:
            await super().stop(*args, **kwargs)
        finally:
            await self.database.close()


def create_app(settings: Settings | None = None) -> HoHoKhanClient:
    return HoHoKhanClient(settings or Settings.from_env())


def run() -> None:
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc

    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("pyrogram.session.session").setLevel(logging.WARNING)
    create_app(settings).run()
