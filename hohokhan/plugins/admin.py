from __future__ import annotations

import asyncio
import html

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from hohokhan.filters import owner_only
from hohokhan.utils.messages import command_argument, handler_errors
from hohokhan.utils.users import resolve_target_user


@Client.on_message(filters.regex(r"^(?:del|حذف)$", flags=2) & owner_only)
@handler_errors
async def delete_replied(_: Client, message: Message) -> None:
    if not message.reply_to_message:
        raise ValueError("روی پیام موردنظر ریپلای کنید")
    await message.reply_to_message.delete()
    await message.delete()


@Client.on_message(filters.regex(r"^\.leave$", flags=2) & owner_only)
@handler_errors
async def leave_chat(client: Client, message: Message) -> None:
    chat_id = message.chat.id
    await message.reply_text("در حال خروج…")
    await client.leave_chat(chat_id)


@Client.on_message(filters.regex(r"^\.join\s+.+", flags=2) & owner_only)
@handler_errors
async def join_chat(client: Client, message: Message) -> None:
    chat = await client.join_chat(command_argument(message))
    await message.reply_text(f"عضو <b>{html.escape(chat.title or str(chat.id))}</b> شدم.")


@Client.on_message(filters.regex(r"^\.add(?:\s|$)", flags=2) & owner_only)
@handler_errors
async def add_member(client: Client, message: Message) -> None:
    user = await resolve_target_user(client, message)
    await client.add_chat_members(message.chat.id, user.id)
    await message.reply_text(f"{user.mention} اضافه شد.")


@Client.on_message(
    (filters.regex(r"^\.kick(?:\s|$)", flags=2) | filters.regex(r"^بن$")) & owner_only
)
@handler_errors
async def kick_member(client: Client, message: Message) -> None:
    user = await resolve_target_user(client, message)
    if user.id in client.settings.sudo_user_ids:
        raise ValueError("کاربر مجاز را نمی‌توان حذف کرد")
    await client.ban_chat_member(message.chat.id, user.id)
    await client.unban_chat_member(message.chat.id, user.id)
    await message.reply_text(f"{user.mention} از گروه حذف شد.")


@Client.on_message(
    (filters.regex(r"^\.mute(?:\s|$)", flags=2) | filters.regex(r"^سکوت$")) & owner_only
)
@handler_errors
async def mute_member(client: Client, message: Message) -> None:
    user = await resolve_target_user(client, message)
    if user.id in client.settings.sudo_user_ids:
        raise ValueError("کاربر مجاز را نمی‌توان محدود کرد")
    await client.restrict_chat_member(
        message.chat.id,
        user.id,
        ChatPermissions(can_send_messages=False),
    )
    await message.reply_text(f"{user.mention} ساکت شد.")


@Client.on_message(
    (filters.regex(r"^\.unmute(?:\s|$)", flags=2) | filters.regex(r"^حذف سکوت$")) & owner_only
)
@handler_errors
async def unmute_member(client: Client, message: Message) -> None:
    user = await resolve_target_user(client, message)
    await client.restrict_chat_member(
        message.chat.id,
        user.id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_invite_users=True,
        ),
    )
    await message.reply_text(f"محدودیت {user.mention} برداشته شد.")


@Client.on_message(filters.regex(r"^قفل گروه$") & owner_only)
@handler_errors
async def lock_chat(client: Client, message: Message) -> None:
    await client.set_chat_permissions(message.chat.id, ChatPermissions(can_send_messages=False))
    await message.reply_text("🔒 ارسال پیام در گروه قفل شد.")


@Client.on_message(filters.regex(r"^باز کردن گروه$") & owner_only)
@handler_errors
async def unlock_chat(client: Client, message: Message) -> None:
    await client.set_chat_permissions(
        message.chat.id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_invite_users=True,
        ),
    )
    await message.reply_text("🔓 ارسال پیام در گروه باز شد.")


@Client.on_message(filters.regex(r"^(?:tag|تگ)$", flags=2) & owner_only)
@handler_errors
async def mention_members(client: Client, message: Message) -> None:
    batch: list[str] = []
    sent = 0
    async for member in client.get_chat_members(message.chat.id):
        user = member.user
        if user.is_bot or user.is_deleted:
            continue
        batch.append(f'<a href="tg://user?id={user.id}">&#8203;</a>')
        sent += 1
        if len(batch) == 5:
            await message.reply_text(" ".join(batch))
            batch.clear()
            await asyncio.sleep(1)
        if sent >= 100:
            break
    if batch:
        await message.reply_text(" ".join(batch))
    await message.reply_text(f"{sent} نفر منشن شدند (سقف هر اجرا: ۱۰۰).")


@Client.on_message(filters.regex(r"^block(?:\s|$)", flags=2) & owner_only)
@handler_errors
async def block_user(client: Client, message: Message) -> None:
    user = await resolve_target_user(client, message)
    if user.id in client.settings.sudo_user_ids:
        raise ValueError("کاربر مجاز را نمی‌توان مسدود کرد")
    await client.block_user(user.id)
    await client.database.set_blocked(user.id, True)
    await message.reply_text(f"{user.mention} مسدود شد.")


@Client.on_message(filters.regex(r"^unblock(?:\s|$)", flags=2) & owner_only)
@handler_errors
async def unblock_user(client: Client, message: Message) -> None:
    user = await resolve_target_user(client, message)
    await client.unblock_user(user.id)
    await client.database.set_blocked(user.id, False)
    await message.reply_text(f"{user.mention} از مسدودی خارج شد.")
