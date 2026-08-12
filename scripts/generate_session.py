from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from pyrogram import Client


async def main() -> None:
    load_dotenv()
    try:
        api_id = int(os.environ["API_ID"])
        api_hash = os.environ["API_HASH"].strip()
    except (KeyError, ValueError) as exc:
        raise SystemExit("API_ID and API_HASH must be set in .env") from exc

    print("Login data is sent directly to Telegram. Never share the resulting session string.")
    app = Client("session-generator", api_id=api_id, api_hash=api_hash, in_memory=True)
    async with app:
        session_string = await app.export_session_string()
    print("\nSESSION_STRING=" + session_string)


if __name__ == "__main__":
    asyncio.run(main())
