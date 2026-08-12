from __future__ import annotations

from pathlib import Path

import aiosqlite


class Database:
    """Asynchronous SQLite store for local, non-secret userbot state."""

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
            CREATE TABLE IF NOT EXISTS notes (
                name TEXT PRIMARY KEY COLLATE NOCASE,
                content TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS afk_state (
                singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                reason TEXT NOT NULL,
                since TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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

    async def set_note(self, name: str, content: str) -> None:
        await self.connection.execute(
            """
            INSERT INTO notes(name, content) VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET
                content=excluded.content,
                updated_at=CURRENT_TIMESTAMP
            """,
            (name.strip(), content.strip()),
        )
        await self.connection.commit()

    async def get_note(self, name: str) -> str | None:
        cursor = await self.connection.execute(
            "SELECT content FROM notes WHERE name = ? COLLATE NOCASE", (name.strip(),)
        )
        row = await cursor.fetchone()
        return str(row["content"]) if row else None

    async def delete_note(self, name: str) -> bool:
        cursor = await self.connection.execute(
            "DELETE FROM notes WHERE name = ? COLLATE NOCASE", (name.strip(),)
        )
        await self.connection.commit()
        return cursor.rowcount > 0

    async def list_notes(self, limit: int = 200) -> list[str]:
        cursor = await self.connection.execute(
            "SELECT name FROM notes ORDER BY name COLLATE NOCASE LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [str(row["name"]) for row in rows]

    async def set_afk(self, reason: str) -> None:
        await self.connection.execute(
            """
            INSERT INTO afk_state(singleton, reason) VALUES (1, ?)
            ON CONFLICT(singleton) DO UPDATE SET
                reason=excluded.reason,
                since=CURRENT_TIMESTAMP
            """,
            (reason.strip(),),
        )
        await self.connection.commit()

    async def get_afk(self) -> tuple[str, str] | None:
        cursor = await self.connection.execute(
            "SELECT reason, since FROM afk_state WHERE singleton = 1"
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return str(row["reason"]), str(row["since"])

    async def clear_afk(self) -> bool:
        cursor = await self.connection.execute("DELETE FROM afk_state WHERE singleton = 1")
        await self.connection.commit()
        return cursor.rowcount > 0
