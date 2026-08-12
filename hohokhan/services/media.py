from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from yt_dlp.utils import DownloadError

from hohokhan.config import Settings
from hohokhan.media_errors import MediaDownloadError, download_error_message
from hohokhan.utils.files import ensure_size, find_downloaded_media

logger = logging.getLogger(__name__)

ALLOWED_MEDIA_HOSTS = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
        "instagram.com",
        "www.instagram.com",
        "tiktok.com",
        "www.tiktok.com",
        "vm.tiktok.com",
        "vt.tiktok.com",
        "twitter.com",
        "www.twitter.com",
        "x.com",
        "www.x.com",
        "likee.video",
        "www.likee.video",
        "radiojavan.com",
        "www.radiojavan.com",
    }
)


@dataclass(frozen=True, slots=True)
class DownloadedMedia:
    path: Path
    title: str
    uploader: str | None
    duration: int | None
    webpage_url: str | None


@dataclass(frozen=True, slots=True)
class SearchResult:
    title: str
    url: str
    uploader: str | None
    duration: int | None


def is_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.hostname)


def is_supported_media_url(value: str) -> bool:
    if not is_url(value):
        return False
    hostname = (urlparse(value.strip()).hostname or "").lower().rstrip(".")
    return hostname in ALLOWED_MEDIA_HOSTS


class MediaDownloader:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _network_options(self) -> dict:
        options: dict = {
            "js_runtimes": {"node": {}},
            "sleep_interval_requests": 1,
        }
        if self.settings.ytdlp_cookies_file:
            options["cookiefile"] = str(self.settings.ytdlp_cookies_file)
        return options

    def _common_options(self, output_dir: Path) -> dict:
        options: dict = {
            **self._network_options(),
            "outtmpl": str(output_dir / "%(title).160B [%(id)s].%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "retries": 3,
            "fragment_retries": 3,
            "socket_timeout": 30,
            "max_filesize": self.settings.max_download_bytes,
            "windowsfilenames": True,
            "restrictfilenames": False,
            "overwrites": False,
            "continuedl": False,
            "match_filter": self._match_filter,
        }
        sleep = self.settings.ytdlp_sleep_interval_seconds
        if sleep:
            options["sleep_interval"] = sleep
            options["max_sleep_interval"] = sleep + 5
        return options

    def _extract_info(
        self, downloader: yt_dlp.YoutubeDL, target: str, *, download: bool
    ) -> dict:
        try:
            return downloader.extract_info(target, download=download)
        except DownloadError as exc:
            logger.warning("yt-dlp could not retrieve the requested media")
            raise MediaDownloadError(
                download_error_message(
                    exc,
                    cookies_configured=self.settings.ytdlp_cookies_file is not None,
                )
            ) from None

    def _match_filter(self, info: dict, *, incomplete: bool = False) -> str | None:
        duration = info.get("duration")
        if duration and duration > self.settings.max_media_duration_seconds:
            return "media duration exceeds the configured limit"
        if info.get("is_live"):
            return "live streams are not supported"
        return None

    def _download_audio_sync(self, query: str, output_dir: Path) -> DownloadedMedia:
        target = query.strip()
        if is_url(target):
            if not is_supported_media_url(target):
                raise ValueError("این دامنه برای دانلود مجاز نیست")
        else:
            target = f"ytsearch1:{target}"

        options = self._common_options(output_dir)
        options.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    },
                    {"key": "FFmpegMetadata", "add_metadata": True},
                ],
            }
        )
        with yt_dlp.YoutubeDL(options) as downloader:
            info = self._extract_info(downloader, target, download=True)
        if info.get("entries"):
            info = next((item for item in info["entries"] if item), None) or {}
        path = find_downloaded_media(output_dir)
        ensure_size(path, self.settings.max_download_bytes)
        return DownloadedMedia(
            path=path,
            title=str(info.get("track") or info.get("title") or path.stem),
            uploader=info.get("artist") or info.get("uploader"),
            duration=info.get("duration"),
            webpage_url=info.get("webpage_url"),
        )

    def _download_video_sync(self, url: str, output_dir: Path) -> DownloadedMedia:
        if not is_supported_media_url(url):
            raise ValueError("این دامنه برای دانلود مجاز نیست")
        options = self._common_options(output_dir)
        options.update(
            {
                "format": "bv*[height<=720]+ba/b[height<=720]/best[height<=720]/best",
                "merge_output_format": "mp4",
                "postprocessors": [{"key": "FFmpegMetadata", "add_metadata": True}],
            }
        )
        with yt_dlp.YoutubeDL(options) as downloader:
            info = self._extract_info(downloader, url, download=True)
        if info.get("entries"):
            info = next((item for item in info["entries"] if item), None) or {}
        path = find_downloaded_media(output_dir)
        ensure_size(path, self.settings.max_download_bytes)
        return DownloadedMedia(
            path=path,
            title=str(info.get("title") or path.stem),
            uploader=info.get("uploader"),
            duration=info.get("duration"),
            webpage_url=info.get("webpage_url"),
        )

    def _search_sync(self, query: str, limit: int) -> list[SearchResult]:
        options = {
            **self._network_options(),
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": True,
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(options) as downloader:
            data = self._extract_info(
                downloader, f"ytsearch{limit}:{query}", download=False
            )
        results: list[SearchResult] = []
        for item in data.get("entries") or []:
            if not item:
                continue
            video_id = item.get("id")
            url = item.get("url") or (
                f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
            )
            if not url:
                continue
            results.append(
                SearchResult(
                    title=str(item.get("title") or "بدون عنوان"),
                    url=str(url),
                    uploader=item.get("uploader") or item.get("channel"),
                    duration=item.get("duration"),
                )
            )
        return results

    async def download_audio(self, query: str, output_dir: Path) -> DownloadedMedia:
        async with asyncio.timeout(900):
            return await asyncio.to_thread(self._download_audio_sync, query, output_dir)

    async def download_video(self, url: str, output_dir: Path) -> DownloadedMedia:
        async with asyncio.timeout(900):
            return await asyncio.to_thread(self._download_video_sync, url, output_dir)

    async def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        async with asyncio.timeout(60):
            return await asyncio.to_thread(self._search_sync, query, limit)
