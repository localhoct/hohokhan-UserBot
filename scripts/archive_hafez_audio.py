from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

from hohokhan.config import ConfigurationError, Settings
from hohokhan.hafez_archive import (
    HAFEZ_AUDIO_CHAT_ID,
    HAFEZ_AUDIO_CHAT_USERNAME,
    archive_tag,
    find_archived_audio_message_id,
)
from hohokhan.runtime import ensure_runtime
from hohokhan.services.hafez import download_hafez_audio


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload Hafez recitations to the configured Telegram archive channel."
    )
    parser.add_argument("--start", type=int, default=1, choices=range(1, 496))
    parser.add_argument("--end", type=int, default=495, choices=range(1, 496))
    return parser.parse_args()


async def main() -> None:
    ensure_runtime()
    # Import only after asyncio.run() has installed the event loop (Python 3.14).
    from pyrogram import Client

    args = _arguments()
    if args.start > args.end:
        raise SystemExit("--start must be less than or equal to --end")
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    app = Client(
        "hafez-archive",
        api_id=settings.api_id,
        api_hash=settings.api_hash,
        session_string=settings.session_string,
        in_memory=bool(settings.session_string),
        workdir=str(settings.data_dir),
    )
    async with app:
        chat = await app.get_chat(HAFEZ_AUDIO_CHAT_ID)
        print(f"Archive: {chat.title} (@{HAFEZ_AUDIO_CHAT_USERNAME})")
        with TemporaryDirectory(dir=settings.temp_dir) as directory:
            for number in range(args.start, args.end + 1):
                existing = await find_archived_audio_message_id(app, number)
                if existing is not None:
                    print(f"[{number}/495] already archived as message {existing}")
                    continue

                path = Path(directory) / f"hafez-{number}.mp3"
                try:
                    await download_hafez_audio(
                        number, path, settings.max_download_bytes
                    )
                    sent = await app.send_audio(
                        HAFEZ_AUDIO_CHAT_ID,
                        str(path),
                        title=f"غزل شماره {number} حافظ",
                        performer="خوانش غزل حافظ",
                        caption=(
                            f"🪶 خوانش غزل شماره {number} حافظ\n\n"
                            f"{archive_tag(number)} #حافظ"
                        ),
                    )
                    print(f"[{number}/495] uploaded as message {sent.id}")
                finally:
                    path.unlink(missing_ok=True)


if __name__ == "__main__":
    asyncio.run(main())
