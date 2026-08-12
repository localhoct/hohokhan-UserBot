from __future__ import annotations

import html
import platform
import secrets
from time import perf_counter

import psutil
from pyrogram import Client, filters
from pyrogram.types import Message

from hohokhan.filters import owner_only, public_guard
from hohokhan.texts import ANSWERS, HELP_TEXT
from hohokhan.utils.files import human_bytes
from hohokhan.utils.messages import handler_errors


@Client.on_message((filters.regex(r"^(?:\.help|راهنما)$")) & public_guard)
@handler_errors
async def help_command(_: Client, message: Message) -> None:
    await message.reply_text(HELP_TEXT, disable_web_page_preview=True)


@Client.on_message(filters.regex(r"^هو\s*هو(?:\s*خان)?$") & public_guard)
@handler_errors
async def greeting(_: Client, message: Message) -> None:
    await message.reply_text(secrets.choice(ANSWERS))


@Client.on_message(filters.regex(r"^(?:\.?ping)$", flags=2) & public_guard)
@handler_errors
async def ping(_: Client, message: Message) -> None:
    started = perf_counter()
    response = await message.reply_text("پینگ…")
    elapsed_ms = (perf_counter() - started) * 1000
    await response.edit_text(f"🏓 <b>{elapsed_ms:.0f} ms</b>")


@Client.on_message(filters.regex(r"^\.info$") & public_guard)
@handler_errors
async def user_info(client: Client, message: Message) -> None:
    target = (
        message.reply_to_message.from_user
        if message.reply_to_message and message.reply_to_message.from_user
        else message.from_user
    )
    if target is None:
        raise ValueError("اطلاعات کاربر در دسترس نیست")
    user = await client.get_users(target.id)
    name = " ".join(part for part in (user.first_name, user.last_name) if part)
    username = f"@{user.username}" if user.username else "—"
    await message.reply_text(
        "\n".join(
            (
                f"<b>نام:</b> {html.escape(name or '—')}",
                f"<b>شناسه:</b> <code>{user.id}</code>",
                f"<b>نام کاربری:</b> {html.escape(username)}",
                f"<b>DC:</b> <code>{user.dc_id or '—'}</code>",
                f"<b>بات:</b> {'بله' if user.is_bot else 'خیر'}",
            )
        )
    )


@Client.on_message(filters.regex(r"^\.?sysinfo$", flags=2) & owner_only)
@handler_errors
async def system_info(_: Client, message: Message) -> None:
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    await message.reply_text(
        "\n".join(
            (
                f"<b>سیستم:</b> {html.escape(platform.platform())}",
                f"<b>Python:</b> <code>{platform.python_version()}</code>",
                f"<b>CPU:</b> {psutil.cpu_percent(interval=0.2):.0f}%",
                f"<b>RAM:</b> {memory.percent:.0f}% از {human_bytes(memory.total)}",
                f"<b>Disk:</b> {disk.percent:.0f}% از {human_bytes(disk.total)}",
            )
        )
    )
