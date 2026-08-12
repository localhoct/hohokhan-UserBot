from __future__ import annotations

import html
from datetime import UTC, datetime
from time import monotonic

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import Message

from hohokhan.filters import public_guard
from hohokhan.productivity import format_duration
from hohokhan.utils.messages import command_argument, handler_errors

AFK_NOTICE_COOLDOWN_SECONDS = 60


def _elapsed_since(value: str) -> str:
    since = datetime.fromisoformat(value).replace(tzinfo=UTC)
    elapsed = int((datetime.now(UTC) - since).total_seconds())
    return format_duration(elapsed)


def _is_directed_at_owner(message: Message) -> bool:
    if message.chat.type == ChatType.PRIVATE:
        return True
    if bool(getattr(message, "mentioned", False)):
        return True
    replied = message.reply_to_message
    return bool(replied and replied.from_user and replied.from_user.is_self)


@Client.on_message(filters.regex(r"^\.afk(?:\s+.*)?$", flags=2) & filters.outgoing)
@handler_errors
async def enable_afk(client: Client, message: Message) -> None:
    reason = command_argument(message) or "بدون توضیح"
    if len(reason) > 300:
        raise ValueError("دلیل AFK نباید بیشتر از ۳۰۰ نویسه باشد")
    await client.database.set_afk(reason)
    client.afk_notice_cache.clear()
    await message.reply_text(f"🌙 وضعیت AFK فعال شد: {html.escape(reason)}")


@Client.on_message(filters.regex(r"^\.back$", flags=2) & filters.outgoing)
@handler_errors
async def disable_afk(client: Client, message: Message) -> None:
    state = await client.database.get_afk()
    if not state:
        await message.reply_text("وضعیت AFK فعال نیست.")
        return
    await client.database.clear_afk()
    client.afk_notice_cache.clear()
    await message.reply_text(f"☀️ AFK پس از {_elapsed_since(state[1])} غیرفعال شد.")


@Client.on_message(filters.incoming & filters.text & public_guard, group=50)
@handler_errors
async def afk_notice(client: Client, message: Message) -> None:
    if not _is_directed_at_owner(message) or not message.from_user:
        return
    state = await client.database.get_afk()
    if not state:
        return
    key = (message.chat.id, message.from_user.id)
    now = monotonic()
    if now - client.afk_notice_cache.get(key, 0.0) < AFK_NOTICE_COOLDOWN_SECONDS:
        return
    if len(client.afk_notice_cache) > 1_000:
        client.afk_notice_cache.clear()
    client.afk_notice_cache[key] = now
    reason, since = state
    await message.reply_text(
        "\n".join(
            (
                "🌙 کاربر در وضعیت AFK است.",
                f"<b>مدت:</b> {html.escape(_elapsed_since(since))}",
                f"<b>دلیل:</b> {html.escape(reason)}",
            )
        )
    )
