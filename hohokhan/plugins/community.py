from __future__ import annotations

import html

from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter, ChatType
from pyrogram.types import Message

from hohokhan.filters import owner_only, public_guard
from hohokhan.utils.messages import handler_errors

GROUP_TYPES = {ChatType.GROUP, ChatType.SUPERGROUP}


@Client.on_message(filters.regex(r"^\.id$", flags=2) & public_guard)
@handler_errors
async def show_ids(_: Client, message: Message) -> None:
    lines = [
        f"<b>Chat ID:</b> <code>{message.chat.id}</code>",
        f"<b>Message ID:</b> <code>{message.id}</code>",
    ]
    replied = message.reply_to_message
    if replied:
        lines.append(f"<b>Replied message ID:</b> <code>{replied.id}</code>")
        if replied.from_user:
            lines.append(f"<b>User ID:</b> <code>{replied.from_user.id}</code>")
        elif replied.sender_chat:
            lines.append(f"<b>Sender chat ID:</b> <code>{replied.sender_chat.id}</code>")
    elif message.from_user:
        lines.append(f"<b>User ID:</b> <code>{message.from_user.id}</code>")
    await message.reply_text("\n".join(lines))


@Client.on_message(filters.regex(r"^\.chatinfo$", flags=2) & owner_only)
@handler_errors
async def chat_info(client: Client, message: Message) -> None:
    chat = await client.get_chat(message.chat.id)
    username = f"@{chat.username}" if chat.username else "—"
    members = "—"
    if chat.type in GROUP_TYPES or chat.type == ChatType.CHANNEL:
        members = str(await client.get_chat_members_count(chat.id))
    await message.reply_text(
        "\n".join(
            (
                f"<b>عنوان:</b> {html.escape(chat.title or chat.first_name or '—')}",
                f"<b>شناسه:</b> <code>{chat.id}</code>",
                f"<b>نوع:</b> <code>{chat.type.value}</code>",
                f"<b>نام کاربری:</b> {html.escape(username)}",
                f"<b>اعضا:</b> <code>{members}</code>",
            )
        )
    )


@Client.on_message(filters.regex(r"^\.admins$", flags=2) & public_guard)
@handler_errors
async def list_admins(client: Client, message: Message) -> None:
    if message.chat.type not in GROUP_TYPES:
        raise ValueError("این دستور فقط در گروه قابل استفاده است")
    lines = ["<b>مدیران گروه</b>"]
    async for member in client.get_chat_members(
        message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
    ):
        user = member.user
        name = " ".join(part for part in (user.first_name, user.last_name) if part) or "کاربر"
        lines.append(f'• <a href="tg://user?id={user.id}">{html.escape(name)}</a>')
        if len(lines) >= 51:
            break
    await message.reply_text("\n".join(lines))
