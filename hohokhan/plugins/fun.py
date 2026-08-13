from __future__ import annotations

import html
from pathlib import Path
from tempfile import TemporaryDirectory

from pyrogram import Client, filters
from pyrogram.types import Message

from hohokhan.filters import public_guard
from hohokhan.services.hafez import (
    HafezFortune,
    download_hafez_audio,
    get_hafez_fortune,
)
from hohokhan.utils.messages import handler_errors


def _render_fortune(fortune: HafezFortune) -> str:
    interpretation = fortune.interpretation
    while True:
        result = (
            f"🪶 <b>غزل شماره {fortune.number}</b>\n\n"
            f"<blockquote>{html.escape(fortune.poem)}</blockquote>\n\n"
            f"🔮 <b>تعبیر فال</b>\n{html.escape(interpretation)}\n\n"
            "<blockquote>اگر صوت خوانش این غزل را می‌خواهی بنویس: بخونش</blockquote>"
        )
        if len(result) <= 3_900:
            return result
        overflow = len(result) - 3_899
        if overflow >= len(interpretation):
            raise ValueError("متن فال برای ارسال در تلگرام بیش از حد طولانی است")
        interpretation = interpretation[:-overflow].rstrip() + "…"


@Client.on_message(filters.regex(r"^(?:فال|فال حافظ)$", flags=2) & public_guard)
@handler_errors
async def hafez_fortune(client: Client, message: Message) -> None:
    fortune = await get_hafez_fortune()
    user_id = message.from_user.id if message.from_user else 0
    client.hafez_fortunes[(message.chat.id, user_id)] = fortune.number
    await message.reply_text(_render_fortune(fortune))


@Client.on_message(filters.regex(r"^(?:بخونش|بخوانش)$", flags=2) & public_guard)
@handler_errors
async def hafez_audio(client: Client, message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    number = client.hafez_fortunes.get((message.chat.id, user_id))
    if number is None:
        raise ValueError("ابتدا بنویسید «فال» تا غزل شما مشخص شود")
    with TemporaryDirectory(dir=client.settings.temp_dir) as directory:
        path = Path(directory) / f"hafez-{number}.mp3"
        await download_hafez_audio(number, path, client.settings.max_download_bytes)
        await message.reply_audio(
            str(path), title=f"غزل شماره {number} حافظ", performer="خوانش غزل حافظ"
        )


@Client.on_message(filters.regex(r"^(?:تاس|tas)$", flags=2) & public_guard)
@handler_errors
async def dice(_: Client, message: Message) -> None:
    await message.reply_dice(emoji="🎲")


@Client.on_message(filters.regex(r"^(?:دارت|dart)$", flags=2) & public_guard)
@handler_errors
async def dart(_: Client, message: Message) -> None:
    await message.reply_dice(emoji="🎯")


@Client.on_message(
    filters.regex(r"^(?:بسکتبال|بستکتبال|basketball|توپ)$", flags=2) & public_guard
)
@handler_errors
async def basketball(_: Client, message: Message) -> None:
    await message.reply_dice(emoji="🏀")
