from __future__ import annotations

import html

from pyrogram import Client, filters
from pyrogram.types import Message

from hohokhan.filters import owner_only, public_guard
from hohokhan.utils.messages import command_argument, handler_errors


@Client.on_message(filters.regex(r"^addans(?:\s|$)", flags=2) & owner_only)
@handler_errors
async def add_answer(client: Client, message: Message) -> None:
    argument = command_argument(message)
    if "|" in argument:
        trigger, response = (part.strip() for part in argument.split("|", 1))
    elif message.reply_to_message and message.reply_to_message.text and argument:
        trigger, response = message.reply_to_message.text.strip(), argument
    else:
        raise ValueError("فرمت صحیح: addans محرک | پاسخ")
    if not trigger or not response:
        raise ValueError("محرک و پاسخ نباید خالی باشند")
    if len(trigger) > 500 or len(response) > 4000:
        raise ValueError("محرک یا پاسخ بیش از حد طولانی است")
    await client.database.set_reply(trigger, response)
    await message.reply_text(f"پاسخ برای <code>{html.escape(trigger)}</code> ذخیره شد.")


@Client.on_message(filters.regex(r"^delans(?:\s|$)", flags=2) & owner_only)
@handler_errors
async def delete_answer(client: Client, message: Message) -> None:
    trigger = command_argument(message)
    if not trigger:
        raise ValueError("محرک را بعد از delans بنویسید")
    deleted = await client.database.delete_reply(trigger)
    await message.reply_text("حذف شد." if deleted else "چنین پاسخی پیدا نشد.")


@Client.on_message(filters.regex(r"^anslist$", flags=2) & owner_only)
@handler_errors
async def answer_list(client: Client, message: Message) -> None:
    rows = await client.database.list_replies()
    if not rows:
        await message.reply_text("فهرست پاسخ‌ها خالی است.")
        return
    lines = ["<b>پاسخ‌های خودکار</b>"]
    for index, (trigger, response) in enumerate(rows, start=1):
        lines.append(
            f"{index}. <code>{html.escape(trigger)}</code> ← {html.escape(response[:120])}"
        )
    await message.reply_text("\n".join(lines[:101]))


@Client.on_message(filters.regex(r"^cleanans$", flags=2) & owner_only)
@handler_errors
async def clear_answers(client: Client, message: Message) -> None:
    count = await client.database.clear_replies()
    await message.reply_text(f"{count} پاسخ حذف شد.")


@Client.on_message(filters.incoming & filters.text & public_guard, group=100)
@handler_errors
async def automatic_answer(client: Client, message: Message) -> None:
    text = (message.text or "").strip()
    if not text or len(text) > 500:
        return
    response = await client.database.get_reply(text)
    if response:
        await message.reply_text(response)
