from __future__ import annotations

import html

from pyrogram import Client, filters
from pyrogram.types import Message

from hohokhan.filters import owner_only
from hohokhan.productivity import normalize_note_name
from hohokhan.utils.messages import command_argument, handler_errors


@Client.on_message(filters.regex(r"^\.save(?:\s|$)", flags=2) & owner_only)
@handler_errors
async def save_note(client: Client, message: Message) -> None:
    argument = command_argument(message)
    if not argument:
        raise ValueError("فرمت صحیح: .save نام متن؛ یا روی یک پیام ریپلای کنید")
    name_part, separator, inline_content = argument.partition(" ")
    name = normalize_note_name(name_part)
    replied = message.reply_to_message
    content = inline_content.strip() if separator else ""
    if not content and replied:
        content = (replied.text or replied.caption or "").strip()
    if not content:
        raise ValueError("متن یادداشت را بنویسید یا روی یک پیام متنی ریپلای کنید")
    if len(content) > 3_500:
        raise ValueError("متن یادداشت نباید بیشتر از ۳۵۰۰ نویسه باشد")
    await client.database.set_note(name, content)
    await message.reply_text(f"📝 یادداشت <code>{html.escape(name)}</code> ذخیره شد.")


@Client.on_message(filters.regex(r"^\.note(?:\s|$)", flags=2) & owner_only)
@handler_errors
async def show_note(client: Client, message: Message) -> None:
    name = normalize_note_name(command_argument(message))
    content = await client.database.get_note(name)
    if content is None:
        raise ValueError("یادداشتی با این نام پیدا نشد")
    await message.reply_text(
        f"<b>📝 {html.escape(name)}</b>\n\n{html.escape(content)}",
        disable_web_page_preview=True,
    )


@Client.on_message(filters.regex(r"^\.notes$", flags=2) & owner_only)
@handler_errors
async def list_notes(client: Client, message: Message) -> None:
    names = await client.database.list_notes()
    if not names:
        await message.reply_text("فهرست یادداشت‌ها خالی است.")
        return
    rendered = "، ".join(f"<code>{html.escape(name)}</code>" for name in names)
    await message.reply_text(f"<b>یادداشت‌ها ({len(names)})</b>\n{rendered}")


@Client.on_message(filters.regex(r"^\.delnote(?:\s|$)", flags=2) & owner_only)
@handler_errors
async def delete_note(client: Client, message: Message) -> None:
    name = normalize_note_name(command_argument(message))
    deleted = await client.database.delete_note(name)
    await message.reply_text("یادداشت حذف شد." if deleted else "چنین یادداشتی وجود ندارد.")
