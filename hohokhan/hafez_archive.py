from __future__ import annotations

import re
from collections.abc import AsyncIterator
from typing import Protocol

HAFEZ_AUDIO_CHAT_ID = -1003967959794
HAFEZ_AUDIO_CHAT_USERNAME = "Hafez_Ghazals"

_ARCHIVE_TAG_RE = re.compile(r"(?:^|\s)#غزل_(\d{1,3})(?:\s|$)")


def archive_tag(number: int) -> str:
    """Return the stable caption tag used to index an archived recitation."""

    if not 1 <= number <= 495:
        raise ValueError("شماره غزل معتبر نیست")
    return f"#غزل_{number}"


def archived_ghazal_number(caption: str | None) -> int | None:
    """Read a ghazal number from an archive caption, if it is valid."""

    match = _ARCHIVE_TAG_RE.search(caption or "")
    if not match:
        return None
    number = int(match.group(1))
    return number if 1 <= number <= 495 else None


class ArchiveSearchClient(Protocol):
    def search_messages(
        self, chat_id: int, *, query: str, limit: int
    ) -> AsyncIterator[object]: ...


async def find_archived_audio_message_id(
    client: ArchiveSearchClient, number: int
) -> int | None:
    """Find the exact archive message instead of relying on fragile message ordering."""

    tag = archive_tag(number)
    async for candidate in client.search_messages(
        HAFEZ_AUDIO_CHAT_ID, query=tag, limit=10
    ):
        caption = getattr(candidate, "caption", None)
        audio = getattr(candidate, "audio", None)
        if audio is not None and archived_ghazal_number(caption) == number:
            message_id = getattr(candidate, "id", None)
            if isinstance(message_id, int):
                return message_id
    return None
