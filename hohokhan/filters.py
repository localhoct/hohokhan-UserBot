from __future__ import annotations

from pyrogram import filters
from pyrogram.types import Message


async def _owner_only(_, client, message: Message) -> bool:  # type: ignore[no-untyped-def]
    user = message.from_user
    return bool(message.outgoing or (user and user.id in client.settings.sudo_user_ids))


async def _public_guard(_, client, message: Message) -> bool:  # type: ignore[no-untyped-def]
    user = message.from_user
    if user is None:
        return False
    if message.outgoing or user.id in client.settings.sudo_user_ids:
        return True
    if await client.database.is_blocked(user.id):
        return False
    return client.rate_limiter.check(user.id).allowed


owner_only = filters.create(_owner_only, "OwnerOnly")
public_guard = filters.create(_public_guard, "PublicGuard")
