from __future__ import annotations


class MediaDownloadError(ValueError):
    """A safe, user-facing media download error."""


def download_error_message(error: object, *, cookies_configured: bool) -> str:
    """Translate noisy yt-dlp errors without exposing implementation details."""

    detail = str(error).casefold().replace("’", "'")
    authentication_markers = (
        "sign in to confirm you're not a bot",
        "use --cookies-from-browser or --cookies",
        "login required",
        "members-only content",
        "confirm your age",
    )
    if any(marker in detail for marker in authentication_markers):
        if cookies_configured:
            return (
                "کوکی YouTube پذیرفته نشد یا منقضی شده است. یک cookies.txt تازه "
                "طبق بخش «رفع محدودیت YouTube» در README صادر کنید و ربات را دوباره اجرا کنید."
            )
        return (
            "YouTube این IP را به بررسی ضدربات فرستاده است. یک cookies.txt معتبر بسازید، "
            "مسیرش را در YTDLP_COOKIES_FILE قرار دهید و ربات را دوباره اجرا کنید؛ "
            "جزئیات در README آمده است."
        )

    return "دانلود رسانه ناموفق بود؛ لینک، دسترسی محتوا و تنظیمات yt-dlp را بررسی کنید."
