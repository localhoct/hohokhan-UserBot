from __future__ import annotations

import asyncio
import html

from pyrogram import Client, filters
from pyrogram.types import Message

from hohokhan.filters import owner_only, public_guard
from hohokhan.utils.messages import command_argument, handler_errors

MAX_PURGE_MESSAGES = 100


def _quote_author(message: Message) -> str:
    if message.from_user:
        name = " ".join(
            part for part in (message.from_user.first_name, message.from_user.last_name) if part
        ) or "کاربر"
        return f'<a href="tg://user?id={message.from_user.id}">{html.escape(name)}</a>'
    if message.sender_chat:
        return html.escape(message.sender_chat.title or "فرستنده ناشناس")
    return "فرستنده ناشناس"


@Client.on_message(filters.regex(r"^\.quote$", flags=2) & public_guard)
@handler_errors
async def quote_message(_: Client, message: Message) -> None:
    replied = message.reply_to_message
    if not replied:
        raise ValueError("روی یک پیام متنی ریپلای کنید")
    content = (replied.text or replied.caption or "").strip()
    if not content:
        raise ValueError("پیام ریپلای‌شده متن یا کپشن ندارد")
    if len(content) > 3_000:
        content = content[:3_000] + "…"
    date = replied.date.strftime("%Y-%m-%d %H:%M UTC")
    await message.reply_text(
        f"❝\n{html.escape(content)}\n❞\n"
        f"— {_quote_author(replied)} · <code>{date}</code>",
        disable_web_page_preview=True,
    )


async def _recent_message_ids(client: Client, message: Message, count: int) -> list[int]:
    ids: list[int] = []
    async for item in client.get_chat_history(message.chat.id, limit=count):
        ids.append(item.id)
    return ids


@Client.on_message(filters.regex(r"^\.purge(?:\s+\d+)?$", flags=2) & owner_only)
@handler_errors
async def purge_messages(client: Client, message: Message) -> None:
    argument = command_argument(message)
    if message.reply_to_message:
        span = message.id - message.reply_to_message.id + 1
        if span < 1 or span > MAX_PURGE_MESSAGES:
            raise ValueError("بازه حذف باید بین ۱ تا ۱۰۰ پیام باشد")
        message_ids = list(range(message.reply_to_message.id, message.id + 1))
    else:
        if not argument:
            raise ValueError("روی ابتدای بازه ریپلای کنید یا تعداد را بنویسید")
        count = int(argument)
        if not 1 <= count <= MAX_PURGE_MESSAGES:
            raise ValueError("تعداد حذف باید بین ۱ تا ۱۰۰ باشد")
        message_ids = await _recent_message_ids(client, message, count)
    if not message_ids:
        raise ValueError("پیامی برای حذف پیدا نشد")
    deleted = await client.delete_messages(message.chat.id, message_ids)
    status = await client.send_message(message.chat.id, f"🧹 {deleted} پیام حذف شد.")
    await asyncio.sleep(2)
    await status.delete()
