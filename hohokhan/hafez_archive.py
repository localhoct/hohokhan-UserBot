from __future__ import annotations

import re
from collections.abc import AsyncIterator
from typing import Protocol

HAFEZ_AUDIO_CHAT_ID = -1003967959794
HAFEZ_AUDIO_CHAT_USERNAME = "Hafez_Ghazals"

_ARCHIVE_NUMBER_PATTERNS = (
    re.compile(r"(?:^|\s)#غزل_(\d{1,3})(?:\s|$)"),
    re.compile(r"غزل(?:\s+شماره)?[\s_:\-]*(\d{1,3})"),
    re.compile(r"hafez[\s_\-]*(\d{1,3})", re.I),
)


def archive_tag(number: int) -> str:
    """Return the stable caption tag used to index an archived recitation."""

    if not 1 <= number <= 495:
        raise ValueError("شماره غزل معتبر نیست")
    return f"#غزل_{number}"


def archived_ghazal_number(*values: str | None) -> int | None:
    """Read a valid ghazal number from caption, audio title, or filename."""

    for value in values:
        for pattern in _ARCHIVE_NUMBER_PATTERNS:
            match = pattern.search(value or "")
            if match:
                number = int(match.group(1))
                if 1 <= number <= 495:
                    return number
    return None


class ArchiveSearchClient(Protocol):
    def search_messages(
        self, chat_id: int, *, query: str, limit: int
    ) -> AsyncIterator[object]: ...

    def get_chat_history(self, chat_id: int, *, limit: int) -> AsyncIterator[object]: ...


def _message_ghazal_number(message: object) -> int | None:
    audio = getattr(message, "audio", None)
    if audio is None:
        return None
    return archived_ghazal_number(
        getattr(message, "caption", None),
        getattr(audio, "title", None),
        getattr(audio, "file_name", None),
    )


async def load_archive_index(client: ArchiveSearchClient) -> dict[int, int]:
    """Build a complete index without depending on Telegram's search index."""

    result: dict[int, int] = {}
    async for message in client.get_chat_history(HAFEZ_AUDIO_CHAT_ID, limit=2_000):
        number = _message_ghazal_number(message)
        message_id = getattr(message, "id", None)
        if number is not None and isinstance(message_id, int):
            result.setdefault(number, message_id)
            if len(result) == 495:
                break
    return result


async def find_archived_audio_message_id(
    client: ArchiveSearchClient, number: int
) -> int | None:
    """Find the exact archive message instead of relying on fragile message ordering."""

    tag = archive_tag(number)
    async for candidate in client.search_messages(
        HAFEZ_AUDIO_CHAT_ID, query=tag, limit=10
    ):
        if _message_ghazal_number(candidate) == number:
            message_id = getattr(candidate, "id", None)
            if isinstance(message_id, int):
                return message_id
    return None
