from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

import httpx

HAFEZ_BASE_URL = "https://hafez.taktemp.com"
HAFEZ_GHAZAL_COUNT = 495
USER_AGENT = "HoHoKhan/2.2 (https://github.com/localhoct/hohokhan-UserBot)"
_REFERENCE_RE = re.compile(r"(?:fals|music)/([1-9]\d{0,2})\.(?:txt|mp3)", re.I)


@dataclass(frozen=True, slots=True)
class HafezFortune:
    number: int
    poem: str
    interpretation: str


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"br", "p", "div", "li", "h1", "h2", "h3", "hr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "div", "li", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def decode_hafez_payload(content: bytes) -> str:
    """Decode legacy endpoint bytes without trusting its incorrect HTTP charset."""

    for encoding in ("utf-8-sig", "windows-1256"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")


def _repair_mojibake(value: str) -> str:
    """Repair UTF-8 text that was previously decoded as Latin-1/Windows-1252."""

    if not any(marker in value for marker in ("Ø", "Ù", "Ú", "Û", "â€")):
        return value
    try:
        repaired = value.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        try:
            repaired = value.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return value
    return repaired


def _plain_text(raw: str) -> str:
    parser = _VisibleText()
    parser.feed(_repair_mojibake(raw))
    return "".join(parser.parts)


def parse_hafez_fortune(raw: str, number: int) -> HafezFortune:
    """Parse the text/HTML payload served by the legacy Hafez endpoint."""

    visible = _plain_text(raw.replace("\ufeff", ""))
    lines = [re.sub(r"\s+", " ", line).strip() for line in visible.splitlines()]
    lines = [line for line in lines if line]
    marker = next(
        (
            index
            for index, line in enumerate(lines)
            if line == "===" or "تعبیر" in line or "تفسير" in line
        ),
        None,
    )
    if marker is None:
        raise ValueError("پاسخ سرویس فال ساختار قابل‌خواندن ندارد")

    poem_lines = [
        line
        for line in lines[:marker]
        if line not in {"غزل", "نمایش کامل غزل", "نمایش کامل غزل ↓"}
    ]
    interpretation_lines = [
        line
        for line in lines[marker + 1 :]
        if line not in {"نمایش کامل تعبیر", "نمایش کامل تعبیر ↓"}
    ]
    if not poem_lines or not interpretation_lines:
        raise ValueError("متن غزل یا تعبیر فال دریافت نشد")
    return HafezFortune(
        number=number,
        poem="\n".join(poem_lines),
        interpretation="\n".join(interpretation_lines),
    )


def _number_from_landing_page(raw: str) -> int | None:
    match = _REFERENCE_RE.search(raw)
    if not match:
        return None
    number = int(match.group(1))
    return number if 1 <= number <= HAFEZ_GHAZAL_COUNT else None


async def get_hafez_fortune() -> HafezFortune:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,text/plain"}
    try:
        async with httpx.AsyncClient(timeout=20, headers=headers, follow_redirects=True) as client:
            landing = await client.get(f"{HAFEZ_BASE_URL}/fal.htm")
            landing.raise_for_status()
            preferred = _number_from_landing_page(decode_hafez_payload(landing.content))
            numbers = [preferred] if preferred else []
            while len(numbers) < 4:
                candidate = secrets.randbelow(HAFEZ_GHAZAL_COUNT) + 1
                if candidate not in numbers:
                    numbers.append(candidate)
            for number in numbers:
                response = await client.get(f"{HAFEZ_BASE_URL}/fals/{number}.txt")
                if response.status_code == 404:
                    continue
                response.raise_for_status()
                if len(response.content) > 256 * 1024:
                    raise ValueError("پاسخ سرویس فال بیش از حد بزرگ است")
                return parse_hafez_fortune(decode_hafez_payload(response.content), number)
    except httpx.HTTPError as exc:
        raise ValueError("سرویس فال حافظ موقتاً در دسترس نیست") from exc
    raise ValueError("فال معتبری از سرویس دریافت نشد")


async def download_hafez_audio(number: int, destination: Path, maximum: int) -> Path:
    if not 1 <= number <= HAFEZ_GHAZAL_COUNT:
        raise ValueError("شماره غزل معتبر نیست")
    headers = {"User-Agent": USER_AGENT, "Accept": "audio/mpeg,audio/*"}
    total = 0
    try:
        async with httpx.AsyncClient(timeout=60, headers=headers, follow_redirects=True) as client:
            async with client.stream(
                "GET", f"{HAFEZ_BASE_URL}/music/{number}.mp3"
            ) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").casefold()
                if content_type and not (
                    content_type.startswith("audio/")
                    or content_type.startswith("application/octet-stream")
                ):
                    raise ValueError("پاسخ سرویس، فایل صوتی معتبر نیست")
                with destination.open("wb") as output:
                    async for chunk in response.aiter_bytes():
                        total += len(chunk)
                        if total > maximum:
                            raise ValueError("فایل صوتی غزل بیش از حد مجاز است")
                        output.write(chunk)
    except httpx.HTTPError as exc:
        destination.unlink(missing_ok=True)
        raise ValueError("فایل صوتی این غزل در دسترس نیست") from exc
    if total == 0:
        destination.unlink(missing_ok=True)
        raise ValueError("فایل صوتی این غزل خالی است")
    return destination

