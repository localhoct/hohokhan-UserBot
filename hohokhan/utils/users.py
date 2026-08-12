from __future__ import annotations

from pyrogram.types import Message, User

from hohokhan.utils.messages import command_argument


async def resolve_target_user(client, message: Message) -> User:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    argument = command_argument(message)
    if not argument:
        raise ValueError("روی پیام کاربر ریپلای کنید یا شناسه/نام کاربری را بنویسید")
    return await client.get_users(argument)
