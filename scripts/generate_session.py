from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from hohokhan.runtime import ensure_runtime


async def main() -> None:
    ensure_runtime()
    # Import after asyncio.run() has installed the running loop. Kurigram exports
    # the Pyrogram-compatible package under the original `pyrogram` namespace.
    from pyrogram import Client

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
    try:
        asyncio.run(main())
    except RuntimeError as exc:
        raise SystemExit(f"Runtime error: {exc}") from exc
