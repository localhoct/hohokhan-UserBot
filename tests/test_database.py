import importlib.util
import tempfile
import unittest
from pathlib import Path

AIOSQLITE_AVAILABLE = importlib.util.find_spec("aiosqlite") is not None
if AIOSQLITE_AVAILABLE:
    from hohokhan.database import Database


@unittest.skipUnless(AIOSQLITE_AVAILABLE, "aiosqlite is not installed in this test runner")
class DatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.directory.name) / "test.sqlite3")
        await self.database.connect()

    async def asyncTearDown(self) -> None:
        await self.database.close()
        self.directory.cleanup()

    async def test_note_lifecycle_is_case_insensitive(self) -> None:
        await self.database.set_note("Server", "example.test")
        self.assertEqual(await self.database.get_note("server"), "example.test")
        self.assertEqual(await self.database.list_notes(), ["Server"])
        self.assertTrue(await self.database.delete_note("SERVER"))
        self.assertIsNone(await self.database.get_note("server"))

    async def test_afk_lifecycle(self) -> None:
        self.assertIsNone(await self.database.get_afk())
        await self.database.set_afk("جلسه")
        state = await self.database.get_afk()
        self.assertIsNotNone(state)
        assert state is not None
        self.assertEqual(state[0], "جلسه")
        self.assertTrue(await self.database.clear_afk())
        self.assertIsNone(await self.database.get_afk())
