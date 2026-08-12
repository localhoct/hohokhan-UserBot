from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from hohokhan.filters import public_guard
from hohokhan.help import render_help
from hohokhan.utils.messages import command_argument, handler_errors


@Client.on_message(
    filters.regex(r"^(?:\.help|راهنما)(?:\s+.*)?$", flags=2) & public_guard
)
@handler_errors
async def help_command(_: Client, message: Message) -> None:
    pages = render_help(command_argument(message))
    for page in pages:
        await message.reply_text(page, disable_web_page_preview=True)
