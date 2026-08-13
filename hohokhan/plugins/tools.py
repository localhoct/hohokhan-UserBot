from __future__ import annotations

import asyncio
import base64
import codecs
import hashlib
import html
import ipaddress
import secrets
import string
from pathlib import Path
from tempfile import TemporaryDirectory

import pytesseract
import qrcode
from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message

from hohokhan.commands import weather_city
from hohokhan.filters import public_guard
from hohokhan.services.ovpn import replace_remote_hosts
from hohokhan.services.web import current_weather, wikipedia_summary
from hohokhan.utils.messages import command_argument, handler_errors


@Client.on_message(filters.regex(r"^\.wiki\s+.+", flags=2) & public_guard)
@handler_errors
async def wiki(_: Client, message: Message) -> None:
    result = await wikipedia_summary(command_argument(message))
    if result is None:
        raise ValueError("مقاله‌ای پیدا نشد")
    summary, url = result
    suffix = f'\n\n<a href="{html.escape(url, quote=True)}">مطالعه کامل</a>' if url else ""
    await message.reply_text(html.escape(summary) + suffix, disable_web_page_preview=True)


@Client.on_message(
    (
        filters.regex(r"^\.weather\s+.+", flags=2)
        | filters.regex(r"^(?:آب\s*و\s*هوای?|هوای?)\s+.+", flags=2)
    )
    & public_guard
)
@handler_errors
async def weather(client: Client, message: Message) -> None:
    if not client.settings.openweather_api_key:
        raise ValueError("OPENWEATHER_API_KEY تنظیم نشده است")
    city = weather_city(message.text or message.caption or "")
    data = await current_weather(city, client.settings.openweather_api_key)
    await message.reply_text(
        "\n".join(
            (
                f"🌤 <b>{html.escape(data.city)}</b> — {html.escape(data.description)}",
                f"دما: <b>{data.temperature:.1f}°C</b>",
                f"دمای احساسی: {data.feels_like:.1f}°C",
                f"رطوبت: {data.humidity}%",
                f"سرعت باد: {data.wind_speed:.1f} m/s",
            )
        )
    )


@Client.on_message(filters.regex(r"^\.qr(?:\s+.*)?$", flags=2) & public_guard)
@handler_errors
async def qr_code(client: Client, message: Message) -> None:
    text = command_argument(message)
    if text:
        with TemporaryDirectory(dir=client.settings.temp_dir) as directory:
            path = Path(directory) / "qrcode.png"
            image = await asyncio.to_thread(qrcode.make, text)
            await asyncio.to_thread(image.save, path)
            await message.reply_document(str(path), caption="QR ساخته شد.")
        return

    replied = message.reply_to_message
    if not replied or not (
        replied.photo or (replied.document and replied.document.mime_type == "image/png")
    ):
        raise ValueError("متنی بنویسید یا روی تصویر QR ریپلای کنید")
    with TemporaryDirectory(dir=client.settings.temp_dir) as directory:
        path = Path(await replied.download(file_name=str(Path(directory) / "qr-image")))
        try:
            from pyzbar.pyzbar import decode as decode_qr
        except ImportError as exc:
            raise ValueError("کتابخانه سیستمی libzbar نصب نیست") from exc
        decoded = await asyncio.to_thread(lambda: decode_qr(Image.open(path)))
        if not decoded:
            raise ValueError("QR قابل‌خواندن پیدا نشد")
        values = [item.data.decode("utf-8", errors="replace") for item in decoded[:5]]
        await message.reply_text("\n\n".join(html.escape(value) for value in values))


@Client.on_message(filters.regex(r"^ocr$", flags=2) & public_guard)
@handler_errors
async def ocr(client: Client, message: Message) -> None:
    replied = message.reply_to_message
    if not replied or not replied.photo:
        raise ValueError("روی یک عکس ریپلای کنید")
    with TemporaryDirectory(dir=client.settings.temp_dir) as directory:
        path = Path(await replied.download(file_name=str(Path(directory) / "ocr.jpg")))
        text = await asyncio.to_thread(
            pytesseract.image_to_string, Image.open(path), lang="fas+eng"
        )
    if not text.strip():
        raise ValueError("متنی در تصویر تشخیص داده نشد")
    await message.reply_text(f"<pre>{html.escape(text[:3900])}</pre>")


@Client.on_message(filters.regex(r"^(?:\.photo|عکس|استیکر به عکس)$") & public_guard)
@handler_errors
async def sticker_to_photo(client: Client, message: Message) -> None:
    replied = message.reply_to_message
    if not replied or not replied.sticker:
        raise ValueError("روی یک استیکر ثابت ریپلای کنید")
    if replied.sticker.is_animated or replied.sticker.is_video:
        raise ValueError("در این نسخه فقط استیکر ثابت پشتیبانی می‌شود")
    with TemporaryDirectory(dir=client.settings.temp_dir) as directory:
        source = Path(await replied.download(file_name=str(Path(directory) / "sticker.webp")))
        destination = Path(directory) / "sticker.png"
        await asyncio.to_thread(lambda: Image.open(source).convert("RGBA").save(destination, "PNG"))
        await message.reply_document(str(destination))


@Client.on_message(filters.regex(r"^(?:\.sticker|\.stik|استیکر|عکس به استیکر)$") & public_guard)
@handler_errors
async def photo_to_sticker(client: Client, message: Message) -> None:
    replied = message.reply_to_message
    if not replied or not replied.photo:
        raise ValueError("روی یک عکس ریپلای کنید")
    with TemporaryDirectory(dir=client.settings.temp_dir) as directory:
        source = Path(await replied.download(file_name=str(Path(directory) / "photo.jpg")))
        destination = Path(directory) / "sticker.webp"

        def convert() -> None:
            image = Image.open(source).convert("RGBA")
            image.thumbnail((512, 512), Image.Resampling.LANCZOS)
            image.save(destination, "WEBP", quality=90, method=6)

        await asyncio.to_thread(convert)
        await message.reply_sticker(str(destination))


@Client.on_message(filters.regex(r"^\.hash\s+.+", flags=2) & public_guard)
@handler_errors
async def hash_text(_: Client, message: Message) -> None:
    argument = command_argument(message)
    parts = argument.split(maxsplit=1)
    if len(parts) != 2:
        raise ValueError("فرمت صحیح: .hash sha256 متن")
    algorithm, text = parts
    if algorithm.lower() not in {"md5", "sha1", "sha224", "sha256", "sha384", "sha512"}:
        raise ValueError("الگوریتم مجاز نیست")
    digest = hashlib.new(algorithm.lower(), text.encode("utf-8")).hexdigest()
    await message.reply_text(f"<code>{digest}</code>")


@Client.on_message(filters.regex(r"^\.pass(?:\s+\d+)?$", flags=2) & public_guard)
@handler_errors
async def password(_: Client, message: Message) -> None:
    argument = command_argument(message)
    length = int(argument) if argument else 20
    if not 8 <= length <= 128:
        raise ValueError("طول رمز باید بین ۸ و ۱۲۸ باشد")
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*_-+="
    value = "".join(secrets.choice(alphabet) for _ in range(length))
    await message.reply_text(f"<code>{html.escape(value)}</code>")


@Client.on_message(filters.regex(r"^\.rot13\s+.+", flags=2) & public_guard)
@handler_errors
async def rot13(_: Client, message: Message) -> None:
    await message.reply_text(
        f"<code>{html.escape(codecs.encode(command_argument(message), 'rot_13'))}</code>"
    )


@Client.on_message(filters.regex(r"^\.(?:encode|decode)(?:\s+.*)?$", flags=2) & public_guard)
@handler_errors
async def base64_codec(_: Client, message: Message) -> None:
    command = (message.text or "").split(maxsplit=1)[0].lower()
    value = command_argument(message)
    if not value and message.reply_to_message:
        value = message.reply_to_message.text or ""
    if not value:
        raise ValueError("متن را بنویسید یا روی آن ریپلای کنید")
    if command == ".encode":
        result = base64.urlsafe_b64encode(value.encode()).decode()
    else:
        try:
            result = base64.urlsafe_b64decode(value.encode()).decode("utf-8")
        except Exception as exc:
            raise ValueError("متن Base64 معتبر نیست") from exc
    await message.reply_text(f"<code>{html.escape(result)}</code>")


@Client.on_message(filters.regex(r"^\.ips\s+\S+$", flags=2) & public_guard)
@handler_errors
async def subnet(_: Client, message: Message) -> None:
    network = ipaddress.ip_network(command_argument(message), strict=False)
    hosts = max(
        0, network.num_addresses - (2 if network.version == 4 and network.prefixlen < 31 else 0)
    )
    await message.reply_text(
        "\n".join(
            (
                f"<b>Network:</b> <code>{network.network_address}</code>",
                f"<b>Broadcast:</b> <code>{network.broadcast_address}</code>",
                f"<b>Netmask:</b> <code>{network.netmask}</code>",
                f"<b>Prefix:</b> <code>/{network.prefixlen}</code>",
                f"<b>Usable hosts:</b> <code>{hosts}</code>",
            )
        )
    )


@Client.on_message(filters.document & public_guard, group=10)
@handler_errors
async def ovpn_document(client: Client, message: Message) -> None:
    document = message.document
    if not document or not (document.file_name or "").lower().endswith(".ovpn"):
        return
    if document.file_size and document.file_size > 1024 * 1024:
        raise ValueError("فایل OVPN نباید بیشتر از ۱ مگابایت باشد")
    with TemporaryDirectory(dir=client.settings.temp_dir) as directory:
        source = Path(await message.download(file_name=str(Path(directory) / "input.ovpn")))
        destination = Path(directory) / "resolved.ovpn"
        replacements = await replace_remote_hosts(source, destination)
        caption = "\n".join(
            f"<code>{html.escape(host)}</code> → <code>{ip}</code>" for host, ip in replacements
        )
        await message.reply_document(str(destination), caption=caption[:1000])
