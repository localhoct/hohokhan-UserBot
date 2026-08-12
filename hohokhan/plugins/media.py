from __future__ import annotations

import html
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from pyrogram import Client, filters
from pyrogram.types import Message

from hohokhan.filters import public_guard
from hohokhan.services.media import MediaDownloader, is_supported_media_url
from hohokhan.utils.files import safe_filename
from hohokhan.utils.messages import command_argument, handler_errors

logger = logging.getLogger(__name__)


async def _archive(client: Client, sent_message: Message) -> None:
    archive = client.settings.media_archive_chat_id
    if archive:
        try:
            await sent_message.copy(archive)
        except Exception:
            logger.exception("Could not archive media message")


@Client.on_message(filters.regex(r"^(?:\.music|آهنگ|اهنگ)\s+.+", flags=2) & public_guard)
@handler_errors
async def download_music(client: Client, message: Message) -> None:
    query = command_argument(message)
    if not query:
        raise ValueError("بعد از دستور، نام آهنگ یا لینک را بنویسید")

    status = await message.reply_text("🎵 در حال دریافت و پردازش صدا…")
    try:
        async with client.download_semaphore:
            with TemporaryDirectory(dir=client.settings.temp_dir) as directory:
                media = await MediaDownloader(client.settings).download_audio(
                    query, Path(directory)
                )
                sent = await message.reply_audio(
                    str(media.path),
                    title=media.title[:64],
                    performer=(media.uploader or "HoHoKhan")[:64],
                    file_name=safe_filename(f"{media.title}.mp3"),
                    duration=media.duration or 0,
                )
                if sent:
                    await _archive(client, sent)
    finally:
        await status.delete()


@Client.on_message(filters.regex(r"^\.yt\s+.+", flags=2) & public_guard)
@handler_errors
async def search_youtube(client: Client, message: Message) -> None:
    query = command_argument(message)
    results = await MediaDownloader(client.settings).search(query)
    if not results:
        raise ValueError("نتیجه‌ای پیدا نشد")
    lines = ["<b>نتایج YouTube</b>"]
    for index, result in enumerate(results, start=1):
        title = html.escape(result.title)
        uploader = html.escape(result.uploader or "نامشخص")
        lines.append(
            f'{index}. <a href="{html.escape(result.url, quote=True)}">{title}</a> — {uploader}'
        )
    await message.reply_text("\n".join(lines), disable_web_page_preview=True)


@Client.on_message(filters.regex(r"https?://\S+", flags=2) & public_guard, group=5)
@handler_errors
async def download_video_url(client: Client, message: Message) -> None:
    text = message.text or message.caption or ""
    url = next(
        (part.rstrip(".,؛،)") for part in text.split() if is_supported_media_url(part)), None
    )
    if not url:
        return

    status = await message.reply_text("🎬 در حال دریافت و پردازش ویدیو…")
    try:
        async with client.download_semaphore:
            with TemporaryDirectory(dir=client.settings.temp_dir) as directory:
                output_dir = Path(directory)
                media = await MediaDownloader(client.settings).download_video(url, output_dir)
                sent = await message.reply_video(
                    str(media.path),
                    caption=f"<b>{html.escape(media.title)}</b>",
                    duration=media.duration or 0,
                    supports_streaming=True,
                    file_name=safe_filename(media.path.name),
                )
                if sent:
                    await _archive(client, sent)
    finally:
        await status.delete()
