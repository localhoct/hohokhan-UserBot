from __future__ import annotations

import html
import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])
logger = logging.getLogger(__name__)


def command_argument(message: Message) -> str:
    text = message.text or message.caption or ""
    return text.split(maxsplit=1)[1].strip() if len(text.split(maxsplit=1)) == 2 else ""


def escaped(value: object) -> str:
    return html.escape(str(value), quote=True)


def handler_errors(func: F) -> F:
    """Log implementation details while showing users a safe, short error."""

    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):  # type: ignore[no-untyped-def]
        try:
            return await func(client, message, *args, **kwargs)
        except FloodWait as exc:
            await message.reply_text(
                f"تلگرام محدودیت موقت اعمال کرده؛ {exc.value} ثانیه بعد تلاش کنید."
            )
        except (ValueError, FileNotFoundError) as exc:
            await message.reply_text(f"خطا: {escaped(exc)}")
        except RPCError:
            logger.exception("Telegram RPC error in %s", func.__name__)
            await message.reply_text(
                "تلگرام این درخواست را نپذیرفت؛ دسترسی‌ها و ورودی را بررسی کنید."
            )
        except Exception:
            logger.exception("Unhandled error in %s", func.__name__)
            await message.reply_text("اجرای درخواست ناموفق بود. جزئیات در لاگ ثبت شد.")

    return wrapper  # type: ignore[return-value]
