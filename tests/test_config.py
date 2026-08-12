from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hohokhan.config import ConfigurationError, Settings

BASE_ENV = {
    "API_ID": "12345",
    "API_HASH": "abc123",
    "OWNER_ID": "99",
    "DATA_DIR": "./test-data",
    "TEMP_DIR": "./test-tmp",
}


class SettingsTests(unittest.TestCase):
    def test_required_values_and_sudo_ids(self) -> None:
        with patch.dict(os.environ, {**BASE_ENV, "SUDO_USER_IDS": "100, 101"}, clear=True):
            settings = Settings.from_env()
        self.assertEqual(settings.api_id, 12345)
        self.assertEqual(settings.sudo_user_ids, frozenset({99, 100, 101}))
        self.assertEqual(settings.max_download_bytes, 150 * 1024 * 1024)

    def test_missing_api_hash_is_rejected(self) -> None:
        environment = {key: value for key, value in BASE_ENV.items() if key != "API_HASH"}
        with patch.dict(os.environ, environment, clear=True), self.assertRaises(ConfigurationError):
            Settings.from_env()

    def test_invalid_sudo_id_is_rejected(self) -> None:
        with patch.dict(os.environ, {**BASE_ENV, "SUDO_USER_IDS": "not-a-number"}, clear=True):
            with self.assertRaises(ConfigurationError):
                Settings.from_env()

    def test_cookie_file_must_exist(self) -> None:
        environment = {**BASE_ENV, "YTDLP_COOKIES_FILE": "./missing-cookies.txt"}
        with patch.dict(os.environ, environment, clear=True), self.assertRaises(
            ConfigurationError
        ):
            Settings.from_env()

    def test_cookie_file_and_sleep_interval_are_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cookie_file = Path(directory) / "youtube-cookies.txt"
            cookie_file.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
            environment = {
                **BASE_ENV,
                "YTDLP_COOKIES_FILE": str(cookie_file),
                "YTDLP_SLEEP_INTERVAL_SECONDS": "0",
            }
            with patch.dict(os.environ, environment, clear=True):
                settings = Settings.from_env()
        self.assertEqual(settings.ytdlp_cookies_file, cookie_file.resolve())
        self.assertEqual(settings.ytdlp_sleep_interval_seconds, 0)


if __name__ == "__main__":
    unittest.main()
