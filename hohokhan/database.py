from __future__ import annotations

from pathlib import Path

import aiosqlite


class Database:
    """Small asynchronous SQLite store for replies and local block rules."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._connection: aiosqlite.Connection | None = None

    @property
    def connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            raise RuntimeError("database is not connected")
        return self._connection

    async def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = await aiosqlite.connect(self.path)
        self._connection.row_factory = aiosqlite.Row
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA foreign_keys=ON")
        await self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS auto_replies (
                trigger TEXT PRIMARY KEY COLLATE NOCASE,
                response TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS blocked_users (
                user_id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        await self._connection.commit()

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def set_reply(self, trigger: str, response: str) -> None:
        await self.connection.execute(
            """
            INSERT INTO auto_replies(trigger, response) VALUES (?, ?)
            ON CONFLICT(trigger) DO UPDATE SET response=excluded.response
            """,
            (trigger.strip(), response.strip()),
        )
        await self.connection.commit()

    async def get_reply(self, trigger: str) -> str | None:
        cursor = await self.connection.execute(
            "SELECT response FROM auto_replies WHERE trigger = ? COLLATE NOCASE",
            (trigger.strip(),),
        )
        row = await cursor.fetchone()
        return str(row["response"]) if row else None

    async def delete_reply(self, trigger: str) -> bool:
        cursor = await self.connection.execute(
            "DELETE FROM auto_replies WHERE trigger = ? COLLATE NOCASE", (trigger.strip(),)
        )
        await self.connection.commit()
        return cursor.rowcount > 0

    async def list_replies(self, limit: int = 100) -> list[tuple[str, str]]:
        cursor = await self.connection.execute(
            "SELECT trigger, response FROM auto_replies ORDER BY trigger LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [(str(row["trigger"]), str(row["response"])) for row in rows]

    async def clear_replies(self) -> int:
        cursor = await self.connection.execute("DELETE FROM auto_replies")
        await self.connection.commit()
        return cursor.rowcount

    async def set_blocked(self, user_id: int, blocked: bool) -> None:
        if blocked:
            await self.connection.execute(
                "INSERT OR IGNORE INTO blocked_users(user_id) VALUES (?)", (user_id,)
            )
        else:
            await self.connection.execute("DELETE FROM blocked_users WHERE user_id = ?", (user_id,))
        await self.connection.commit()

    async def is_blocked(self, user_id: int) -> bool:
        cursor = await self.connection.execute(
            "SELECT 1 FROM blocked_users WHERE user_id = ?", (user_id,)
        )
        return await cursor.fetchone() is not None
