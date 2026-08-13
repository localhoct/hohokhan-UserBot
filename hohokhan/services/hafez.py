from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import httpx

HAFEZ_SOURCE_URL = "https://divanhafez.com"
HAFEZ_AUDIO_URL = f"{HAFEZ_SOURCE_URL}/app/r{{number}}.mp3"
HAFEZ_GHAZAL_COUNT = 495
HAFEZ_CORPUS_PATH = Path(__file__).resolve().parent.parent / "data" / "hafez_fortunes.json"
USER_AGENT = "HoHoKhan/2.4 (https://github.com/localhoct/hohokhan-UserBot)"


@dataclass(frozen=True, slots=True)
class HafezFortune:
    number: int
    poem: str
    interpretation: str


@lru_cache(maxsize=1)
def load_hafez_corpus(path: Path = HAFEZ_CORPUS_PATH) -> tuple[HafezFortune, ...]:
    """Load and validate the bundled corpus once per process."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("داده داخلی فال حافظ قابل‌خواندن نیست") from exc
    if not isinstance(payload, list) or len(payload) != HAFEZ_GHAZAL_COUNT:
        raise ValueError("داده داخلی فال حافظ باید شامل دقیقاً ۴۹۵ غزل باشد")

    fortunes: list[HafezFortune] = []
    numbers: set[int] = set()
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError("ساختار داده داخلی فال حافظ معتبر نیست")
        try:
            number = int(row["number"])
            poem = str(row["poem"]).strip()
            interpretation = str(row["interpretation"]).strip()
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("یکی از رکوردهای فال حافظ ناقص است") from exc
        if not 1 <= number <= HAFEZ_GHAZAL_COUNT or number in numbers:
            raise ValueError("شماره‌های داده داخلی فال حافظ معتبر یا یکتا نیستند")
        if not poem or not interpretation:
            raise ValueError("متن غزل یا تعبیر داخلی خالی است")
        numbers.add(number)
        fortunes.append(HafezFortune(number, poem, interpretation))

    if numbers != set(range(1, HAFEZ_GHAZAL_COUNT + 1)):
        raise ValueError("برخی شماره‌های غزل در داده داخلی موجود نیستند")
    return tuple(sorted(fortunes, key=lambda fortune: fortune.number))


async def get_hafez_fortune() -> HafezFortune:
    """Return a random bundled fortune without network access."""

    return secrets.choice(load_hafez_corpus())


async def download_hafez_audio(number: int, destination: Path, maximum: int) -> Path:
    if not 1 <= number <= HAFEZ_GHAZAL_COUNT:
        raise ValueError("شماره غزل معتبر نیست")
    headers = {"User-Agent": USER_AGENT, "Accept": "audio/mpeg,audio/*"}
    total = 0
    async with httpx.AsyncClient(timeout=60, headers=headers, follow_redirects=True) as client:
        try:
            async with client.stream("GET", HAFEZ_AUDIO_URL.format(number=number)) as response:
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
        except (httpx.HTTPError, ValueError) as exc:
            destination.unlink(missing_ok=True)
            raise ValueError("فایل صوتی این غزل در دسترس نیست") from exc
    if not total:
        destination.unlink(missing_ok=True)
        raise ValueError("فایل صوتی این غزل خالی است")
    return destination
